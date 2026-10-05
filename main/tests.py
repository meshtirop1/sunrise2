from django.core import mail
from django.test import TestCase

from .models import ContactSubmission, InquiryType, TeamMember


class PublicPagesTest(TestCase):
    """Every public page renders with its database-driven content."""

    def test_pages_return_200(self):
        for url in ['/', '/about/', '/team/', '/services/', '/gallery/', '/contact/']:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_home_shows_editable_content(self):
        response = self.client.get('/')
        self.assertContains(response, 'Sunrise Drilling')

    def test_footer_shows_site_settings(self):
        response = self.client.get('/')
        self.assertContains(response, '+254 720 997 769')
        self.assertContains(response, 'sunrisedrillingltd@gmail.com')

    def test_team_page_seeded_from_profile(self):
        self.assertEqual(TeamMember.objects.count(), 6)
        response = self.client.get('/team/')
        self.assertContains(response, 'Abraham K. Kiptoo')
        self.assertContains(response, 'Managing Director')


class ContactFormTest(TestCase):
    def _post(self, **overrides):
        data = {
            'name': 'Jane Test',
            'email': 'jane@example.com',
            'phone': '0700000000',
            'inquiry_type': 'Drilling of Boreholes',
            'message': 'I need a borehole quote.',
        }
        data.update(overrides)
        return self.client.post('/contact/', data)

    def test_submission_saved_with_db_inquiry_type(self):
        # 'Drilling of Boreholes' comes from the InquiryType table; it used to
        # fail silently when choices were hard-coded in the form.
        self.assertTrue(InquiryType.objects.filter(name='Drilling of Boreholes').exists())
        response = self._post()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you')
        submission = ContactSubmission.objects.get()
        self.assertEqual(submission.inquiry_type, 'Drilling of Boreholes')

    def test_auto_reply_and_notification_sent(self):
        self._post()
        recipients = [addr for m in mail.outbox for addr in m.to]
        self.assertIn('jane@example.com', recipients)  # auto-reply
        self.assertEqual(len(mail.outbox), 2)  # notification + auto-reply

    def test_invalid_email_rejected(self):
        self._post(email='not-an-email')
        self.assertEqual(ContactSubmission.objects.count(), 0)
