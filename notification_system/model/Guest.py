class Guest:
    def __init__(self, id, name, phone_number, payment_due_date, property_identifier, room_no):
        self.id = id
        self.name = name
        self.payment_due_date = payment_due_date
        self.phone_number = phone_number
        self.property_identifier = property_identifier
        self.room_no = room_no

    def to_dict(self):
        return {"id" : self.id, "guest_name" : self.name, "phone_number" : self.phone_number, "property_identifier" : self.property_identifier, "room_no" : self.room_no}
