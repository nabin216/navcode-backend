from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']

    def validate_phone(self, value):
        if value:
            # Remove any non-digit characters
            cleaned_number = ''.join(filter(str.isdigit, value))
            if len(cleaned_number) < 10:
                raise serializers.ValidationError("Phone number must have at least 10 digits.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value.lower()  # Convert email to lowercase 