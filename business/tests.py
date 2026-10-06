from datetime import date

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from .models import Client, Invoice, InvoiceItem, Payment, Proposal, ProposalItem
from .services import (render_invoice_pdf, render_proposal_pdf, render_receipt_pdf,
                       send_invoice_email, send_proposal_email, send_receipt_email)


def make_client():
    return Client.objects.create(name='Test Client', company='Test Co',
                                 email='client@example.com')


class ProposalTest(TestCase):
    def setUp(self):
        self.client_obj = make_client()

    def _proposal(self, **kwargs):
        p = Proposal.objects.create(client=self.client_obj, title='Borehole – Test Site', **kwargs)
        ProposalItem.objects.create(proposal=p, description='Drilling', quantity=100,
                                    unit='m', unit_price=6500)
        return p

    def test_references_autonumber_per_year_and_kind(self):
        p1 = self._proposal()
        p2 = self._proposal()
        q1 = Proposal.objects.create(client=self.client_obj, title='Quote',
                                     kind=Proposal.KIND_QUOTATION)
        year = p1.created_at.year
        self.assertEqual(p1.reference, f'SDL-P-{year}-001')
        self.assertEqual(p2.reference, f'SDL-P-{year}-002')
        self.assertEqual(q1.reference, f'SDL-Q-{year}-001')

    def test_total(self):
        p = self._proposal()
        self.assertEqual(p.total, 650000)

    def test_pdf_renders(self):
        pdf = render_proposal_pdf(self._proposal())
        self.assertTrue(pdf.startswith(b'%PDF'))

    def test_send_marks_sent_and_logs(self):
        p = self._proposal()
        ok, _ = send_proposal_email(p)
        self.assertTrue(ok)
        p.refresh_from_db()
        self.assertEqual(p.status, Proposal.STATUS_SENT)
        self.assertEqual(p.sent_to, 'client@example.com')
        self.assertEqual(p.email_logs.filter(success=True).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['client@example.com'])
        self.assertTrue(mail.outbox[0].attachments)


class InvoicePaymentTest(TestCase):
    def setUp(self):
        self.client_obj = make_client()
        self.invoice = Invoice.objects.create(client=self.client_obj,
                                              title='Phase 1', due_date=date(2030, 1, 1))
        InvoiceItem.objects.create(invoice=self.invoice, description='Drilling',
                                   quantity=1, unit='lot', unit_price=1000000)

    def test_invoice_reference_and_pdf(self):
        self.assertTrue(self.invoice.reference.startswith('SDL-I-'))
        self.assertTrue(render_invoice_pdf(self.invoice).startswith(b'%PDF'))

    def test_payment_lifecycle(self):
        ok, _ = send_invoice_email(self.invoice)
        self.assertTrue(ok)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.STATUS_SENT)

        p1 = Payment.objects.create(invoice=self.invoice, amount=400000, method='mpesa')
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.STATUS_PARTIAL)
        self.assertEqual(self.invoice.balance, 600000)
        self.assertTrue(p1.receipt_number.startswith('SDL-R-'))
        self.assertTrue(render_receipt_pdf(p1).startswith(b'%PDF'))

        ok, _ = send_receipt_email(p1)
        self.assertTrue(ok)
        p1.refresh_from_db()
        self.assertIsNotNone(p1.receipt_sent_at)

        Payment.objects.create(invoice=self.invoice, amount=600000, method='bank')
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.STATUS_PAID)
        self.assertEqual(self.invoice.balance, 0)


class DashboardTest(TestCase):
    def test_requires_staff_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response.url)

    def test_branded_login_page(self):
        response = self.client.get('/dashboard/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Login')

    def test_login_flow_reaches_dashboard(self):
        User.objects.create_user('staff2', password='pw12345', is_staff=True)
        response = self.client.post('/dashboard/login/',
                                    {'username': 'staff2', 'password': 'pw12345'},
                                    follow=True)
        self.assertContains(response, 'Staff Dashboard')

    def test_staff_can_view(self):
        staff = User.objects.create_user('staff', password='x', is_staff=True)
        self.client.force_login(staff)
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Dashboard')

    def test_dashboard_has_charts_and_no_admin_links(self):
        staff = User.objects.create_user('staff', password='x', is_staff=True)
        self.client.force_login(staff)
        response = self.client.get('/dashboard/')
        self.assertContains(response, 'chart-data')
        self.assertContains(response, 'moneyChart')
        self.assertNotContains(response, '/admin/')


class DashboardCrudTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', password='x', is_staff=True)
        self.client.force_login(self.staff)
        self.client_obj = make_client()

    def test_client_create(self):
        response = self.client.post('/dashboard/clients/new/', {
            'name': 'New Person', 'company': '', 'email': 'new@example.com',
            'phone': '', 'address': '', 'notes': '',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Client.objects.filter(email='new@example.com').exists())

    def test_proposal_create_with_items(self):
        data = {
            'kind': 'proposal', 'client': self.client_obj.pk, 'title': 'Dash proposal',
            'introduction': '', 'scope_of_work': '', 'terms': '', 'validity_days': 30,
            'show_prices': 'on',
            'items-TOTAL_FORMS': '1', 'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0', 'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Drilling', 'items-0-quantity': '100',
            'items-0-unit': 'm', 'items-0-unit_price': '6500',
        }
        response = self.client.post('/dashboard/proposals/new/', data, follow=True)
        proposal = Proposal.objects.get(title='Dash proposal')
        self.assertEqual(proposal.total, 650000)
        self.assertContains(response, proposal.reference)

    def test_invoice_payment_and_pdfs(self):
        invoice = Invoice.objects.create(client=self.client_obj, title='Job',
                                         status=Invoice.STATUS_SENT)
        InvoiceItem.objects.create(invoice=invoice, description='Work',
                                   quantity=1, unit='lot', unit_price=500000)
        response = self.client.post(f'/dashboard/invoices/{invoice.pk}/payments/add/', {
            'amount': '200000', 'method': 'mpesa', 'transaction_ref': 'ABC123',
            'received_on': date.today().isoformat(),
        }, follow=True)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.STATUS_PARTIAL)
        payment = invoice.payments.first()
        self.assertContains(response, payment.receipt_number)
        self.assertEqual(self.client.get(f'/dashboard/invoices/{invoice.pk}/pdf/')['Content-Type'],
                         'application/pdf')
        self.assertEqual(self.client.get(f'/dashboard/payments/{payment.pk}/receipt/')['Content-Type'],
                         'application/pdf')

    def test_list_pages_render(self):
        for path in ('/dashboard/proposals/', '/dashboard/invoices/',
                     '/dashboard/projects/', '/dashboard/clients/',
                     '/dashboard/enquiries/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertNotContains(response, '/admin/')

    def test_lists_require_staff(self):
        self.client.logout()
        response = self.client.get('/dashboard/invoices/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response.url)
