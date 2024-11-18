# app/models/forms.py
import uuid
from datetime import datetime
from mongoengine import Document, UUIDField, StringField, DateTimeField, ListField, IntField

class Form(Document):
    """
    Model representing a form with its unique identifier, information, and tracking of filled users.
    """
    form_uuid = UUIDField(default=uuid.uuid4, unique=True)

    form_name = StringField(required=True)
    form_url = StringField(required=True)
    hidden_fields = ListField(StringField(), required=False)
    description = StringField(required=False)

    form_type = StringField(required=True)
    form_limit = IntField(required=True)
    form_time_deadline = DateTimeField(required=False)
    form_department = StringField(required=False)
    form_result_limit = StringField(required=False)

    sent_to = ListField(UUIDField(), required=False)
    filled_by = ListField(UUIDField(), required=False)

    created_date = DateTimeField(default=datetime.utcnow)

    # Meta information
    meta = {'collection': 'forms'}

    def add_sent_to_user(self, user_uuid):
        """
        Add a user to the list of users to whom the form has been sent.
        :param user_uuid: UUID of the user to whom the form is sent.
        """
        self.sent_to.append(user_uuid)
        self.save()

    def add_filled_by_user(self, user_uuid):
        """
        Add a user to the list of users who have filled the form.
        :param user_uuid: UUID of the user who has filled the form.
        """
        self.filled_by.append(user_uuid)
        self.save()

    def search_filled_by_user(self, user_uuid):
        """
        Search a user in the list of users who have filled the form.
        :param user_uuid: UUID of the user to search (string or UUID).
        """
        if not isinstance(user_uuid, uuid.UUID):
            user_uuid = uuid.UUID(user_uuid)

        flag = user_uuid in self.filled_by
        return flag

    @classmethod
    def find_form_by_uuid(cls, form_uuid):
        """
        Retrieve a form by its UUID.
        :param form_uuid: UUID of the form.
        :return: Form object if found, None otherwise.
        """
        return cls.objects(form_uuid=form_uuid).first()