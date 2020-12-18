from models import Category, Business, db, Business_Cat
import json

def time_format(string):
    hrs = int(string[:2:])
    mins = string[2::]
    if hrs > 12 :
        hrs= hrs-12
    else :
        hrs = str(hrs)
    return f"{hrs}:{mins}"

def parse_resp(jsonReq):
        search_list=[]
        for bus in jsonReq["businesses"]:
            bus = Bus_Profile(bus)

            bus.add_bus_from_resp()

            business = Business.query.filter(Business.yelp_id==bus.yelp_id).first()
            bus.add_db_id_to_temp_obj(business.id)
            print(bus.categories)
            bus.add_cat_from_resp()

            search_list.append(bus)
        return search_list


class Bus_Profile:
    def __init__(self,json):
        self.id = None
        self.yelp_id=json["id"]
        self.name = json["name"]
        self.phone = json["display_phone"]
        if not self.phone:
            self.phone = "No Phone Number Available"
        self.rating = json["rating"]
        self.pic = json.get("image_url","https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg")
        self.photos = json.get("photos")
        self.address= json["location"]["display_address"]
        self.local= bool(json.get("is_claimed",False))
        self.yelp_url=json["url"]
        self.categories=[{"name":cat["title"],"alias":cat["alias"]} for cat in json.get("categories")]
        self.services=json['transactions']
        if 'delivery' in self.services:
            self.delivery = True
        if 'pickup' in self.services:
            self.pickup = True

        if json.get('hours'):
            self.hours = self.format_hours((json["hours"][0]["open"])) 
            self.is_open= json['hours'][0]['is_open_now']


    def add_bus_from_resp(self):
        if not Business.query.filter(Business.yelp_id==self.yelp_id).first():
            business = Business(yelp_id=self.yelp_id,name=self.name)
            
            db.session.add(business)
            db.session.commit()
            return self
        return self

    def add_db_id_to_temp_obj(self, db_bus_id):
        self.id = db_bus_id
        return self


    def add_cat_from_resp(self):
        for cat in self.categories:
            print(cat)
            if not Category.query.filter(Category.name==cat['name']).first():
                cat= Category(name=cat['name'], term=cat['alias'])
                db.session.add(cat)
                db.session.commit()

                connector= Business_Cat(cat_id=cat.id, bus_id=self.id)
                db.session.add(connector)
                db.session.commit()
        return self
        
    def format_hours(self,hours):
        week = {
            0:"Mon",
            1:"Tue",
            2:"Wed",
            3:"Thr",
            4:"Fri",
            5:"Sat",
            6:"Sun",
        }
        open = []
        for entry in hours:
          date =(str(week[entry['day']]+" "+ time_format(entry['start'])+' to '+time_format(entry['end'])))
          open.append(date)
        return open



class BusEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__

