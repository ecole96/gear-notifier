from django.db import models
from django.core.validators import RegexValidator
from multiselectfield import MultiSelectField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime, timedelta
import uuid
import pytz

class UserManager(BaseUserManager):
    def create_user(self,email,craigslist_sites,password=None,phone=None,carrier=None,comm_settings='E',is_active=False,is_staff=False,is_superuser=False):
        if not email:
            raise ValueError("An email address is required.")
        if not password:
            raise ValueError("A password is required.")
        if not craigslist_sites:
            raise ValueError("Between one and three Craigslist locations need to be set.")
        if (phone and not carrier) or (not phone and carrier):
            raise ValueError("If you want to use a phone number, both phone and carrier data is required.")
        if (not phone or not carrier) and comm_settings != 'E':
            raise ValueError("Texts can't be sent unless you provide phone and carrier data.")
        user_obj = self.model(
            email = self.normalize_email(email),
            craigslist_sites = craigslist_sites
        )
        user_obj.set_password(password)
        user_obj.phone = phone
        user_obj.carrier = carrier
        user_obj.communication_settings = comm_settings
        user_obj.is_active = is_active
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self,email,craigslist_sites,password=None):
        user = self.create_user(
            email,
            craigslist_sites,
            password=password,
            is_active=True,
            is_staff=True
        )
        return user
    
    def create_superuser(self,email,craigslist_sites,password=None):
        user = self.create_user(
            email,
            craigslist_sites,
            password=password,
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        return user

class User(AbstractBaseUser):
    CL_CHOICES = [('auburn', 'AL: auburn'), ('bham', 'AL: birmingham'), ('dothan', 'AL: dothan'), ('shoals', 'AL: florence / muscle shoals'), ('gadsden', 'AL: gadsden-anniston'), ('huntsville', 'AL: huntsville / decatur'), ('mobile', 'AL: mobile'), ('montgomery', 'AL: montgomery'), ('tuscaloosa', 'AL: tuscaloosa'), ('anchorage', 'AK: anchorage / mat-su'), ('fairbanks', 'AK: fairbanks'), ('kenai', 'AK: kenai peninsula'), ('juneau', 'AK: southeast alaska'), ('flagstaff', 'AZ: flagstaff / sedona'), ('mohave', 'AZ: mohave county'), ('phoenix', 'AZ: phoenix'), ('prescott', 'AZ: prescott'), ('showlow', 'AZ: show low'), ('sierravista', 'AZ: sierra vista'), ('tucson', 'AZ: tucson'), ('yuma', 'AZ: yuma'), ('fayar', 'AR: fayetteville'), ('fortsmith', 'AR: fort smith'), ('jonesboro', 'AR: jonesboro'), ('littlerock', 'AR: little rock'), ('texarkana', 'AR: texarkana'), ('bakersfield', 'CA: bakersfield'), ('chico', 'CA: chico'), ('fresno', 'CA: fresno / madera'), ('goldcountry', 'CA: gold country'), ('hanford', 'CA: hanford-corcoran'), ('humboldt', 'CA: humboldt county'), ('imperial', 'CA: imperial county'), ('inlandempire', 'CA: inland empire'), ('losangeles', 'CA: los angeles'), ('mendocino', 'CA: mendocino county'), ('merced', 'CA: merced'), ('modesto', 'CA: modesto'), ('monterey', 'CA: monterey bay'), ('orangecounty', 'CA: orange county'), ('palmsprings', 'CA: palm springs'), ('redding', 'CA: redding'), ('sacramento', 'CA: sacramento'), ('sandiego', 'CA: san diego'), ('sfbay', 'CA: san francisco bay area'), ('slo', 'CA: san luis obispo'), ('santabarbara', 'CA: santa barbara'), ('santamaria', 'CA: santa maria'), ('siskiyou', 'CA: siskiyou county'), ('stockton', 'CA: stockton'), ('susanville', 'CA: susanville'), ('ventura', 'CA: ventura county'), ('visalia', 'CA: visalia-tulare'), ('yubasutter', 'CA: yuba-sutter'), ('boulder', 'CO: boulder'), ('cosprings', 'CO: colorado springs'), ('denver', 'CO: denver'), ('eastco', 'CO: eastern CO'), ('fortcollins', 'CO: fort collins / north CO'), ('rockies', 'CO: high rockies'), ('pueblo', 'CO: pueblo'), ('westslope', 'CO: western slope'), ('newlondon', 'CT: eastern CT'), ('hartford', 'CT: hartford'), ('newhaven', 'CT: new haven'), ('nwct', 'CT: northwest CT'), ('delaware', 'DE: delaware'), ('washingtondc', 'DC: washington'), ('miami', 'FL: broward county'), ('daytona', 'FL: daytona beach'), ('keys', 'FL: florida keys'), ('fortlauderdale', 'FL: fort lauderdale'), ('fortmyers', 'FL: ft myers / SW florida'), ('gainesville', 'FL: gainesville'), ('cfl', 'FL: heartland florida'), ('jacksonville', 'FL: jacksonville'), ('lakeland', 'FL: lakeland'), ('miami', 'FL: miami / dade'), ('lakecity', 'FL: north central FL'), ('ocala', 'FL: ocala'), ('okaloosa', 'FL: okaloosa / walton'), ('orlando', 'FL: orlando'), ('panamacity', 'FL: panama city'), ('pensacola', 'FL: pensacola'), ('sarasota', 'FL: sarasota-bradenton'), ('miami', 'FL: south florida'), ('spacecoast', 'FL: space coast'), ('staugustine', 'FL: st augustine'), ('tallahassee', 'FL: tallahassee'), ('tampa', 'FL: tampa bay area'), ('treasure', 'FL: treasure coast'), ('miami', 'FL: palm beach county'), ('albanyga', 'GA: albany'), ('athensga', 'GA: athens'), ('atlanta', 'GA: atlanta'), ('augusta', 'GA: augusta'), ('brunswick', 'GA: brunswick'), ('columbusga', 'GA: columbus'), ('macon', 'GA: macon / warner robins'), ('nwga', 'GA: northwest GA'), ('savannah', 'GA: savannah / hinesville'), ('statesboro', 'GA: statesboro'), ('valdosta', 'GA: valdosta'), ('honolulu', 'HI: hawaii'), ('boise', 'ID: boise'), ('eastidaho', 'ID: east idaho'), ('lewiston', 'ID: lewiston / clarkston'), ('twinfalls', 'ID: twin falls'), ('bn', 'IL: bloomington-normal'), ('chambana', 'IL: champaign urbana'), ('chicago', 'IL: chicago'), ('decatur', 'IL: decatur'), ('lasalle', 'IL: la salle co'), ('mattoon', 'IL: mattoon-charleston'), ('peoria', 'IL: peoria'), ('rockford', 'IL: rockford'), ('carbondale', 'IL: southern illinois'), ('springfieldil', 'IL: springfield'), ('quincy', 'IL: western IL'), ('bloomington', 'IN: bloomington'), ('evansville', 'IN: evansville'), ('fortwayne', 'IN: fort wayne'), ('indianapolis', 'IN: indianapolis'), ('kokomo', 'IN: kokomo'), ('tippecanoe', 'IN: lafayette / west lafayette'), ('muncie', 'IN: muncie / anderson'), ('richmondin', 'IN: richmond'), ('southbend', 'IN: south bend / michiana'), ('terrehaute', 'IN: terre haute'), ('ames', 'IA: ames'), ('cedarrapids', 'IA: cedar rapids'), ('desmoines', 'IA: des moines'), ('dubuque', 'IA: dubuque'), ('fortdodge', 'IA: fort dodge'), ('iowacity', 'IA: iowa city'), ('masoncity', 'IA: mason city'), ('quadcities', 'IA: quad cities'), ('siouxcity', 'IA: sioux city'), ('ottumwa', 'IA: southeast IA'), ('waterloo', 'IA: waterloo / cedar falls'), ('lawrence', 'KS: lawrence'), ('ksu', 'KS: manhattan'), ('nwks', 'KS: northwest KS'), ('salina', 'KS: salina'), ('seks', 'KS: southeast KS'), ('swks', 'KS: southwest KS'), ('topeka', 'KS: topeka'), ('wichita', 'KS: wichita'), ('bgky', 'KY: bowling green'), ('eastky', 'KY: eastern kentucky'), ('lexington', 'KY: lexington'), ('louisville', 'KY: louisville'), ('owensboro', 'KY: owensboro'), ('westky', 'KY: western KY'), ('batonrouge', 'LA: baton rouge'), ('cenla', 'LA: central louisiana'), ('houma', 'LA: houma'), ('lafayette', 'LA: lafayette'), ('lakecharles', 'LA: lake charles'), ('monroe', 'LA: monroe'), ('neworleans', 'LA: new orleans'), ('shreveport', 'LA: shreveport'), ('maine', 'ME: maine'), ('annapolis', 'MD: annapolis'), ('baltimore', 'MD: baltimore'), ('easternshore', 'MD: eastern shore'), ('frederick', 'MD: frederick'), ('smd', 'MD: southern maryland'), ('westmd', 'MD: western maryland'), ('boston', 'MA: boston'), ('capecod', 'MA: cape cod / islands'), ('southcoast', 'MA: south coast'), ('westernmass', 'MA: western massachusetts'), ('worcester', 'MA: worcester / central MA'), ('annarbor', 'MI: ann arbor'), ('battlecreek', 'MI: battle creek'), ('centralmich', 'MI: central michigan'), ('detroit', 'MI: detroit metro'), ('flint', 'MI: flint'), ('grandrapids', 'MI: grand rapids'), ('holland', 'MI: holland'), ('jxn', 'MI: jackson'), ('kalamazoo', 'MI: kalamazoo'), ('lansing', 'MI: lansing'), ('monroemi', 'MI: monroe'), ('muskegon', 'MI: muskegon'), ('nmi', 'MI: northern michigan'), ('porthuron', 'MI: port huron'), ('saginaw', 'MI: saginaw-midland-baycity'), ('swmi', 'MI: southwest michigan'), ('thumb', 'MI: the thumb'), ('up', 'MI: upper peninsula'), ('bemidji', 'MN: bemidji'), ('brainerd', 'MN: brainerd'), ('duluth', 'MN: duluth / superior'), ('mankato', 'MN: mankato'), ('minneapolis', 'MN: minneapolis / st paul'), ('rmn', 'MN: rochester'), ('marshall', 'MN: southwest MN'), ('stcloud', 'MN: st cloud'), ('gulfport', 'MS: gulfport / biloxi'), ('hattiesburg', 'MS: hattiesburg'), ('jackson', 'MS: jackson'), ('meridian', 'MS: meridian'), ('northmiss', 'MS: north mississippi'), ('natchez', 'MS: southwest MS'), ('columbiamo', 'MO: columbia / jeff city'), ('joplin', 'MO: joplin'), ('kansascity', 'MO: kansas city'), ('kirksville', 'MO: kirksville'), ('loz', 'MO: lake of the ozarks'), ('semo', 'MO: southeast missouri'), ('springfield', 'MO: springfield'), ('stjoseph', 'MO: st joseph'), ('stlouis', 'MO: st louis'), ('billings', 'MT: billings'), ('bozeman', 'MT: bozeman'), ('butte', 'MT: butte'), ('greatfalls', 'MT: great falls'), ('helena', 'MT: helena'), ('kalispell', 'MT: kalispell'), ('missoula', 'MT: missoula'), ('montana', 'MT: eastern montana'), ('grandisland', 'NE: grand island'), ('lincoln', 'NE: lincoln'), ('northplatte', 'NE: north platte'), ('omaha', 'NE: omaha / council bluffs'), ('scottsbluff', 'NE: scottsbluff / panhandle'), ('elko', 'NV: elko'), ('lasvegas', 'NV: las vegas'), ('reno', 'NV: reno / tahoe'), ('nh', 'NH: new hampshire'), ('cnj', 'NJ: central NJ'), ('jerseyshore', 'NJ: jersey shore'), ('newjersey', 'NJ: north jersey'), ('southjersey', 'NJ: south jersey'), ('albuquerque', 'NM: albuquerque'), ('clovis', 'NM: clovis / portales'), ('farmington', 'NM: farmington'), ('lascruces', 'NM: las cruces'), ('roswell', 'NM: roswell / carlsbad'), ('santafe', 'NM: santa fe / taos'), ('albany', 'NY: albany'), ('binghamton', 'NY: binghamton'), ('buffalo', 'NY: buffalo'), ('catskills', 'NY: catskills'), ('chautauqua', 'NY: chautauqua'), ('elmira', 'NY: elmira-corning'), ('fingerlakes', 'NY: finger lakes'), ('glensfalls', 'NY: glens falls'), ('hudsonvalley', 'NY: hudson valley'), ('ithaca', 'NY: ithaca'), ('longisland', 'NY: long island'), ('newyork', 'NY: new york city'), ('oneonta', 'NY: oneonta'), ('plattsburgh', 'NY: plattsburgh-adirondacks'), ('potsdam', 'NY: potsdam-canton-massena'), ('rochester', 'NY: rochester'), ('syracuse', 'NY: syracuse'), ('twintiers', 'NY: twin tiers NY/PA'), ('utica', 'NY: utica-rome-oneida'), ('watertown', 'NY: watertown'), ('asheville', 'NC: asheville'), ('boone', 'NC: boone'), ('charlotte', 'NC: charlotte'), ('eastnc', 'NC: eastern NC'), ('fayetteville', 'NC: fayetteville'), ('greensboro', 'NC: greensboro'), ('hickory', 'NC: hickory / lenoir'), ('onslow', 'NC: jacksonville'), ('outerbanks', 'NC: outer banks'), ('raleigh', 'NC: raleigh / durham / CH'), ('wilmington', 'NC: wilmington'), ('winstonsalem', 'NC: winston-salem'), ('bismarck', 'ND: bismarck'), ('fargo', 'ND: fargo / moorhead'), ('grandforks', 'ND: grand forks'), ('nd', 'ND: north dakota'), ('akroncanton', 'OH: akron / canton'), ('ashtabula', 'OH: ashtabula'), ('athensohio', 'OH: athens'), ('chillicothe', 'OH: chillicothe'), ('cincinnati', 'OH: cincinnati'), ('cleveland', 'OH: cleveland'), ('columbus', 'OH: columbus'), ('dayton', 'OH: dayton / springfield'), ('limaohio', 'OH: lima / findlay'), ('mansfield', 'OH: mansfield'), ('sandusky', 'OH: sandusky'), ('toledo', 'OH: toledo'), ('tuscarawas', 'OH: tuscarawas co'), ('youngstown', 'OH: youngstown'), ('zanesville', 'OH: zanesville / cambridge'), ('lawton', 'OK: lawton'), ('enid', 'OK: northwest OK'), ('oklahomacity', 'OK: oklahoma city'), ('stillwater', 'OK: stillwater'), ('tulsa', 'OK: tulsa'), ('bend', 'OR: bend'), ('corvallis', 'OR: corvallis/albany'), ('eastoregon', 'OR: east oregon'), ('eugene', 'OR: eugene'), ('klamath', 'OR: klamath falls'), ('medford', 'OR: medford-ashland'), ('oregoncoast', 'OR: oregon coast'), ('portland', 'OR: portland'), ('roseburg', 'OR: roseburg'), ('salem', 'OR: salem'), ('altoona', 'PA: altoona-johnstown'), ('chambersburg', 'PA: cumberland valley'), ('erie', 'PA: erie'), ('harrisburg', 'PA: harrisburg'), ('lancaster', 'PA: lancaster'), ('allentown', 'PA: lehigh valley'), ('meadville', 'PA: meadville'), ('philadelphia', 'PA: philadelphia'), ('pittsburgh', 'PA: pittsburgh'), ('poconos', 'PA: poconos'), ('reading', 'PA: reading'), ('scranton', 'PA: scranton / wilkes-barre'), ('pennstate', 'PA: state college'), ('williamsport', 'PA: williamsport'), ('york', 'PA: york'), ('providence', 'RI: rhode island'), ('charleston', 'SC: charleston'), ('columbia', 'SC: columbia'), ('florencesc', 'SC: florence'), ('greenville', 'SC: greenville / upstate'), ('hiltonhead', 'SC: hilton head'), ('myrtlebeach', 'SC: myrtle beach'), ('nesd', 'SD: northeast SD'), ('csd', 'SD: pierre / central SD'), ('rapidcity', 'SD: rapid city / west SD'), ('siouxfalls', 'SD: sioux falls / SE SD'), ('sd', 'SD: south dakota'), ('chattanooga', 'TN: chattanooga'), ('clarksville', 'TN: clarksville'), ('cookeville', 'TN: cookeville'), ('jacksontn', 'TN: jackson'), ('knoxville', 'TN: knoxville'), ('memphis', 'TN: memphis'), ('nashville', 'TN: nashville'), ('tricities', 'TN: tri-cities'), ('abilene', 'TX: abilene'), ('amarillo', 'TX: amarillo'), ('austin', 'TX: austin'), ('beaumont', 'TX: beaumont / port arthur'), ('brownsville', 'TX: brownsville'), ('collegestation', 'TX: college station'), ('corpuschristi', 'TX: corpus christi'), ('dallas', 'TX: dallas / fort worth'), ('nacogdoches', 'TX: deep east texas'), ('delrio', 'TX: del rio / eagle pass'), ('elpaso', 'TX: el paso'), ('galveston', 'TX: galveston'), ('houston', 'TX: houston'), ('killeen', 'TX: killeen / temple / ft hood'), ('laredo', 'TX: laredo'), ('lubbock', 'TX: lubbock'), ('mcallen', 'TX: mcallen / edinburg'), ('odessa', 'TX: odessa / midland'), ('sanangelo', 'TX: san angelo'), ('sanantonio', 'TX: san antonio'), ('sanmarcos', 'TX: san marcos'), ('bigbend', 'TX: southwest TX'), ('texoma', 'TX: texoma'), ('easttexas', 'TX: tyler / east TX'), ('victoriatx', 'TX: victoria'), ('waco', 'TX: waco'), ('wichitafalls', 'TX: wichita falls'), ('logan', 'UT: logan'), ('ogden', 'UT: ogden-clearfield'), ('provo', 'UT: provo / orem'), ('saltlakecity', 'UT: salt lake city'), ('stgeorge', 'UT: st george'), ('vermont', 'VT: vermont'), ('charlottesville', 'VA: charlottesville'), ('danville', 'VA: danville'), ('fredericksburg', 'VA: fredericksburg'), ('norfolk', 'VA: hampton roads'), ('harrisonburg', 'VA: harrisonburg'), ('lynchburg', 'VA: lynchburg'), ('blacksburg', 'VA: new river valley'), ('richmond', 'VA: richmond'), ('roanoke', 'VA: roanoke'), ('swva', 'VA: southwest VA'), ('winchester', 'VA: winchester'), ('bellingham', 'WA: bellingham'), ('kpr', 'WA: kennewick-pasco-richland'), ('moseslake', 'WA: moses lake'), ('olympic', 'WA: olympic peninsula'), ('pullman', 'WA: pullman / moscow'), ('seattle', 'WA: seattle-tacoma'), ('skagit', 'WA: skagit / island / SJI'), ('spokane', "WA: spokane / coeur d'alene"), ('wenatchee', 'WA: wenatchee'), ('yakima', 'WA: yakima'), ('charlestonwv', 'WV: charleston'), ('martinsburg', 'WV: eastern panhandle'), ('huntington', 'WV: huntington-ashland'), ('morgantown', 'WV: morgantown'), ('wheeling', 'WV: northern panhandle'), ('parkersburg', 'WV: parkersburg-marietta'), ('swv', 'WV: southern WV'), ('wv', 'WV: west virginia (old)'), ('appleton', 'WI: appleton-oshkosh-FDL'), ('eauclaire', 'WI: eau claire'), ('greenbay', 'WI: green bay'), ('janesville', 'WI: janesville'), ('racine', 'WI: kenosha-racine'), ('lacrosse', 'WI: la crosse'), ('madison', 'WI: madison'), ('milwaukee', 'WI: milwaukee'), ('northernwi', 'WI: northern WI'), ('sheboygan', 'WI: sheboygan'), ('wausau', 'WI: wausau'), ('wyoming', 'WY: wyoming')]
    
    CARRIER_CHOICES = [("AT&T","AT&T"),("Verizon","Verizon"),("T-Mobile","T-Mobile"),("Sprint","Sprint")]
    COMM_CHOICES = [("E","Email"),("T","Text"),("B","Email & Text")]

    email = models.EmailField(max_length=100,unique=True,db_index=True)
    craigslist_sites = MultiSelectField(choices=CL_CHOICES,min_choices=1,max_choices=3,max_length=100,help_text="Any sites you selected will be scraped if you enable Craigslist for an entry. No more than three sites can be selected. CTRL + click to select multiple sites.")
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Invalid phone number.")
    phone = models.CharField(validators=[phone_regex],max_length=10,blank=True,null=True,unique=True,default=None,help_text="Only standard 10-digit US/Canada numbers are supported. No dashes, parentheses, or country code.")
    carrier = models.CharField(max_length=40,choices=CARRIER_CHOICES,blank=True,null=True,default=None,help_text="Currently only a limited number of carriers are supported.")
    communication_settings = models.CharField(max_length=1,choices=COMM_CHOICES,default="E",help_text="This is how you will receive your notifications.")
    is_active = models.BooleanField(default=False)
    active_phone = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['craigslist_sites']
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return True
    
    def has_module_perms(self,app_label):
        return True

def hex_uuid():
    return uuid.uuid4().hex

def token_expire():
    dt_raw = datetime.now() + timedelta(hours=1)
    return dt_raw.replace(tzinfo=pytz.timezone("America/Kentucky/Louisville"))

class Token(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    token_type = models.CharField(max_length=1)
    token = models.CharField(max_length=32,default=hex_uuid) 
    expires_at = models.DateTimeField(default=token_expire)

    def __str__(self):
        return ','.join([self.user.email,self.token,self.token_type])
    