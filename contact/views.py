from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Contact
from .serializers import ContactSerializer
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']  # Only allow POST requests

    def get_queryset(self):
        return Contact.objects.none()  # Don't expose any records through GET requests

    def create(self, request, *args, **kwargs):
        logger.info(f"Received contact form submission from: {request.data.get('email')}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Contact form validation failed: {serializer.errors}")
            return Response({
                'status': 'error',
                'message': 'Please check your input and try again.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = serializer.save()
            logger.info(f"Contact form saved successfully: {contact.id}")
            
            # Send email notification
            try:
                email_message = f"""
New Contact Form Submission

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Subject: {contact.subject}

Message:
{contact.message}

This message was sent from the contact form on your website.
                """
                
                send_mail(
                    subject=f'New Contact Form Submission: {contact.subject}',
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
                logger.info(f"Email notification sent for contact: {contact.id}")
            except Exception as e:
                logger.error(f"Failed to send email notification: {str(e)}")
                # Continue execution even if email fails
                pass

            return Response({
                'status': 'success',
                'message': 'Thank you for your message! We will get back to you soon.'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error saving contact form: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
