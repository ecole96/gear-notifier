from django.core.management.base import BaseCommand
from scraping.models import Match, Misc
from users.models import User
from gn_manager.models import Entry
from bs4 import BeautifulSoup
import requests
import urllib.parse as urlparse
import re
from datetime import datetime, timedelta
import feedparser
import math
import os
import tldextract
from django.conf import settings
from django.core.mail import send_mail

class Command(BaseCommand):
    help = "This script is the basis of this project. It goes through each users' queries and sends new listings accordingly. Designed to be ran on a frequent basis."

    def handle(self, *args, **options):
        self.main()

    def main(self):
        misc = Misc.objects.first() if Misc.objects.first() else Misc()
        lastrun_dt = misc.lastrun_dt.replace(tzinfo=None)
        misc.save()
        users = User.objects.filter(is_active=True)
        rv = Reverb(os.environ['REVERB_API'])
        gc = GuitarCenter()
        cl = Craigslist()
        for user in users:
            try:
                print("\n***",user.email,"***")
                entries = Entry.objects.filter(user=user)
                feed = Feed()
                for entry in entries:
                    site_dict = {"Reverb":entry.rv,"Guitar Center":entry.gc,"Craigslist":entry.cl}
                    sitestr = '/'.join([sitename for sitename in site_dict if site_dict[sitename]])
                    print('Gathering for "' + entry.query + '"',"(Min:",str(entry.min_price)+",","Max:",str(entry.max_price)+", Sites:",sitestr+")")
                    feed.gatherListings(entry,lastrun_dt,rv,gc,cl,user.craigslist_sites)
                    if not entry.initiallyScanned:
                        entry.initiallyScanned = True
                        entry.save()
                    print(len(feed.listings[entry.query]),"listings\n")
                    feed.printListings(entry=entry)
                feed.notifyUser(user)
                print('========================================================================================================================')
            except Exception as e:
                print("Aborting scan for",user.email,"due to error:",e)

def download(url):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    request = requests.get(url,headers={'User-Agent':user_agent})
    page = request.content
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def getDomain(url):
    ext = tldextract.extract(url)
    source = ext.domain
    return source.lower()

# convert local datetime to UTC and return it as a datetime object for comparisons (applicable to Craigsist & Reverb)
def convert_datetime(datestr):
    dt_regex = re.match(r'(^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})-(\d{2}):\d{2}$',datestr).groups()
    utc_offset = int(dt_regex[1])
    return datetime.strptime(dt_regex[0],"%Y-%m-%dT%H:%M:%S") + timedelta(hours=utc_offset)

class Feed:
    def __init__(self):
        self.listings = {}
    
    def gatherListings(self,entry,lastrun_dt,rv,gc,cl,cl_locs):
        if entry.rv: self.listings[entry.query] = rv.search(entry,lastrun_dt)
        if entry.gc: self.listings[entry.query] = gc.search(entry)
        if entry.cl: self.listings[entry.query] = cl.search(entry,cl_locs,lastrun_dt)

    def notifyUser(self,user):
        if any([self.listings[key] for key in self.listings]):
            msgs = self.generateMessage()
            subject = "Gear Notifier - New Listings"
            if user.communication_settings in ['T','B'] and user.active_phone:
                carrier_domains = {'AT&T':'mms.att.net','Verizon':'vzwpix.com','Sprint':'pm.sprint.com','T-Mobile':'tmomail.net'}
                mailto = user.phone + "@" + carrier_domains[user.carrier]
                for msg in msgs:
                    self.send_msg(subject,msg,mailto)
            if user.communication_settings in ['E','B']:
                msg = ''.join(msgs)
                mailto = user.email
                self.send_msg(subject,msg,mailto)
    
    def send_msg(self,subject,msg,mailto):
        try:
            print("Emailing",mailto + "...")
            send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [mailto])
        except Exception as e:
            print("Message failed to send:",e)

    def generateMessage(self):
        curr_msg_index = 0
        messages = ["Here's some new gear listings you might be interested in:\n\n"]
        lst = []
        for key in self.listings:
            for value in self.listings[key]:
                lst.append(value)
        for i,listing in enumerate(lst):
            listing_str = listing.itemMessage()
            if i < len(lst)-1: 
                listing_str += "\n\n"
            if len(messages[curr_msg_index] + listing_str) > 1600:
                messages.append("\n")
                curr_msg_index += 1
            messages[curr_msg_index] += listing_str
        return messages
    
    def printListings(self,entry=None):
        if not entry:
            lst = []
            for key in self.listings:
                for value in self.listings[key]:
                    lst.append(value)
        else:
            lst = self.listings[entry.query]
        for l in lst:
            print(l.itemMessage()+'\n')

class Listing:
    def __init__(self,title,price,shipping,url):
        self.title = title
        self.price = price
        self.shipping = shipping
        self.url = url

    def isDuplicate(self,entry):
        return Match.objects.filter(entry=entry,url=self.url).exists()

    def itemMessage(self):
        item_str = self.title + " - $" + format(self.price, '.2f') + " ("
        if self.shipping is None:
            if getDomain(self.url) in ['craigslist','reverb']:
                item_str += "Local Pickup"
            else:
                item_str += "check site for S/H"
        else:
            item_str += ("+$" + format(self.shipping, '.2f') + " S/H")
        item_str += ")\n" + self.url
        return item_str

class Reverb:
    baseURL = "https://api.reverb.com/api"

    def __init__(self,token):
        self.s = requests.Session()
        self.s.headers.update({"Authorization":"Bearer " + token, "Accept":"application/hal+json","Accept-Version":"3.0"})

    def search(self,entry,lastrun_timestamp):
        url = self.baseURL + "/listings/?query=" + urlparse.quote(entry.query) + "&item_region=US&sort=published_at%7Cdesc"
        if entry.min_price is not None:
            url += "&price_min=" + str(entry.min_price)
        if entry.max_price is not None:
            url += "&price_max=" + str(entry.max_price)
        listings = self.get_matching_listings(url,lastrun_timestamp)
        return listings
    
    def get_matching_listings(self,url,lastrun_dt):
        listings = []
        keepSearching = True
        while keepSearching:
            r = self.s.get(url)
            json = r.json()
            for l in json['listings']:
                listing_dt = convert_datetime(l['created_at'])
                if listing_dt < lastrun_dt:
                    keepSearching = False
                    break
                title = l['title']
                price = l['price']['amount']
                listing_url = l['_links']['web']['href']
                shipping = l['shipping']['rates'][0]['rate']['amount'] if l['shipping']['rates'] else None
                listing = Listing(title,price,shipping,listing_url)
                listings.append(listing)
            if 'next' in json['_links']:
                url = json['_links']['next']['href']
            else:
                keepSearching = False
        return listings

class GuitarCenter:
    baseURL = "https://www.guitarcenter.com"

    def search(self,entry):
        i = 0
        listings = []
        #price_query_str = self.generate_price_criteria(entry.min_price,entry.max_price)
        url = self.baseURL + "/search?typeAheadSuggestion=false&typeAheadRedirect=false&Ntt=" + urlparse.quote_plus(entry.query)
        keepSearching = True
        while keepSearching:
            #url = self.baseURL + "/search?typeAheadSuggestion=false&typeAheadRedirect=false&recsPerPage=90&Nao=" + str(i * 90) + price_query_str + "&Ntt=" + urlparse.quote_plus(entry.query)
            soup = download(url)
            if not soup.select_one("section[id=zeroResultsContent]"):
                products = soup.select("li.product-container")
                for p in products:
                    pt = p.select_one("div.productTitle a")
                    title = pt.text.strip()
                    print(title)
                    listing_url = self.baseURL + pt['href'].replace(' ','+')
                    pr = p.select_one("span.productPrice")
                    for span in pr.select("span"): span.decompose()
                    price = float(pr.text.strip().replace(',',''))
                    if not((entry.min_price is not None and price < entry.min_price) or (entry.max_price is not None and price > entry.max_price)):
                        listing = Listing(title,price,None,listing_url)
                        listings.append(listing)
                nextPage = soup.select_one("a.-next")
                if nextPage:
                    url = self.baseURL + nextPage['href']
                else:
                    keepSearching = False
            else:
                keepSearching = False
        listings = self.cleanup(listings,entry)
        return listings

    # this may not be used
    def generate_price_criteria(self,min_price,max_price):
        price_query_str = ""
        if min_price is not None or max_price is not None:
            price_tiers = { "1081":25,"1082":50,"1083":100,"1084":200,"1085":300,"1086":500,"1087":750,"1088":1000,"1089":1500,"1090":2000,"1091":3000,"1092":5000,
                            "1093":7500, "1094":15000, "1095":50000,"1096":999999999 }
            minkey = 1081
            maxkey = 1096
            if min_price is not None:
                for key in price_tiers:
                    if min_price < price_tiers[key]:
                        minkey = int(key)
                        break
            if max_price is not None:
                for key in price_tiers:
                    if max_price and max_price < price_tiers[key]:
                        maxkey = int(key)
                        break
            price_query_str = "&N=" + '+'.join([str(i) for i in range(minkey,maxkey+1)])
        return price_query_str
        
    def cleanup(self,listings,entry):
        if not entry.initiallyScanned: # first run of entry - save results to database but don't count them as a listing as we're only saving them to know they already exist (so empty out listings array)
            print("Initial entry run...saving old GC listings ["+ str(len(listings)) +"]")
            for l in listings: Match(entry=entry,url=l.url).save()
            listings = []
        else:
            saved_listings = Match.objects.filter(entry=entry)
            listing_urls = [listing.url for listing in listings]
            for sl in saved_listings: 
                if sl.url not in listing_urls: # deletes listings previously saved that no longer appear (gone from GC's site so likely sold or unavailable).
                    sl.delete()
            listings = [l for l in listings if not l.isDuplicate(entry)]
            for l in listings:
                    Match(entry=entry,url=l.url).save() # save new entries
        return listings

class Craigslist():
    baseURL = "craigslist.org"

    def search(self,entry,cl_locs,lastrun_dt):
        listings = []
        url_query = "/search/msa?format=rss&sort=date&query=" + urlparse.quote_plus(entry.query)
        if entry.min_price is not None:
            url_query += "&min_price=" + str(math.floor(entry.min_price))
        if entry.max_price is not None:
            url_query += "&max_price=" + str(math.floor(entry.max_price))
        for location in cl_locs:
                url = "https://" + location + "." + self.baseURL + url_query
                rss = feedparser.parse(url)
                products = rss.entries
                for p in products:
                    listing_dt = convert_datetime(p['published'])
                    if listing_dt < lastrun_dt: 
                        break
                    t = re.match(r'(^.+?)(?= &#x0024;(\d+)|$)',p['title'].strip()).groups()
                    title = t[0]
                    price = float(t[1]) if t[1] else 0.0
                    url = p['id']
                    listing = Listing(title,price,None,url)
                    listings.append(listing)
        return listings