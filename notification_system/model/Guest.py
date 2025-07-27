class Guest:
    def __init__(self, id, name, phone_number, payment_due_date, payment_final_due_date, contract_start_date, contract_end_date, property_identifier, room_no, room_rate):
        self.id = id
        self.name = name
        self.payment_due_date = payment_due_date
        self.payment_final_due_date = payment_final_due_date
        self.phone_number = phone_number
        self.property_identifier = property_identifier
        self.room_no = room_no
        self.contract_start_date = contract_start_date
        self.contract_end_date = contract_end_date
        self.room_rate = room_rate

    def to_dict(self):
        return {"id" : self.id, "guest_name" : self.name, "phone_number" : self.phone_number, "property_identifier" : self.property_identifier, "room_no" : self.room_no}
