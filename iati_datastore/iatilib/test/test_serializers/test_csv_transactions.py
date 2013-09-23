import datetime
from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin
from iatilib.test import factories as fac

from iatilib.frontend import serialize
from iatilib import codelists as cl


class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.transaction_csv(data)


def example():
    activity = fac.ActivityFactory.build(
        iati_identifier="GB-1-123",
        title="Project 123",
        description="Desc project 123",
        recipient_country_percentages=[
            fac.CountryPercentageFactory.build(
                country=cl.Country.kenya,
                percentage=80,
            ),
            fac.CountryPercentageFactory.build(
                country=cl.Country.uganda,
                percentage=20,
            )
        ],
        sector_percentages=[
            fac.SectorPercentageFactory.build(
                sector=cl.Sector.teacher_training,
                percentage=60
            ),
            fac.SectorPercentageFactory.build(
                sector=cl.Sector.primary_education,
                percentage=40
            ),

        ]
    )

    transactions = [
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 6, 30),
            value_amount=10000,
        ),
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 9, 30),
            value_amount=90000,
        ),
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 1, 31),
            value_amount=30000,
        ),
    ]
    for trans in transactions:
        trans.activity = activity
    activity.transactions = transactions
    return activity


class TestCSVTransactionExample(TestCase, CSVTstMixin):
    def test_column_list(self):
        data = self.process([
            fac.TransactionFactory.build()
        ])
        cols = [
            "transaction-type",
            "transaction-date",
            "default-currency",
            "transaction-value",

            "iati-identifier",
            "hierarchy",
            "last-updated-datetime",
            "default-language",
            "reporting-org",
            "reporting-org-ref",
            "reporting-org-type",
            "title",
            "description",
            "activity-status-code",
            "start-planned",
            "end-planned",
            "start-actual",
            "end-actual",
            "participating-org (Accountable)",
            "participating-org-ref (Accountable)",
            "participating-org-type (Accountable)",
            "participating-org (Funding)",
            "participating-org-ref (Funding)",
            "participating-org-type (Funding)",
            "participating-org (Extending)",
            "participating-org-ref (Extending)",
            "participating-org-type (Extending)",
            "participating-org (Implementing)",
            "participating-org-ref (Implementing)",
            "participating-org-type (Implementing)",
            "recipient-country-code",
            "recipient-country",
            "recipient-country-percentage",
            "recipient-region-code",
            "recipient-region",
            "recipient-region-percentage",
            "sector-code",
            "sector",
            "sector-percentage",
            "sector-vocabulary",
            "collaboration-type-code",
            "default-finance-type-code",
            "default-flow-type-code",
            "default-aid-type-code",
            "default-tied-status-code",
            'transaction_ref',
            'transaction_value_currency',
            'transaction_value_value-date',
            'transaction_provider-org',
            'transaction_provider-org_ref',
            'transaction_provider-org_provider-activity-id',
            'transaction_receiver-org',
            'transaction_receiver-org_ref',
            'transaction_receiver-org_receiver-activity-id',
            'transaction_description',
            'transaction_flow-type_code',
            'transaction_finance-type_code',
            'transaction_aid-type_code',
            'transaction_tied-status_code',
            'transaction_disbursement-channel_code',
        ]
        for col in cols:
            self.assertIn(col, data[0].keys(), msg="Missing col %s" % col)

    # See example here: https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c&usp=sharing#gid=5
    def test_transaction_type(self):
        data = self.process([
            fac.TransactionFactory.build(type=cl.TransactionType.disbursement)
        ])
        self.assertField({"transaction-type": "D"}, data[0])

    def test_transaction_type2(self):
        data = self.process([
            fac.TransactionFactory.build(type=cl.TransactionType.commitment)
        ])
        self.assertField({"transaction-type": "C"}, data[0])

    def test_transaction_date(self):
        data = self.process([
            fac.TransactionFactory.build(date=datetime.date(2012, 6, 30))
        ])
        self.assertField({"transaction-date": "2012-06-30"}, data[0])

    def test_default_currency(self):
        data = self.process([
            fac.TransactionFactory.build(
                type=cl.TransactionType.disbursement,
                activity__default_currency=cl.Currency.us_dollar)
        ])
        self.assertField({"default-currency": "USD"}, data[0])

    def test_currency(self):
        # I'm assuming they want the actual currency
        data = self.process([
            fac.TransactionFactory.build(
                type=cl.TransactionType.disbursement,
                value_currency=cl.Currency.australian_dollar)
        ])
        self.assertField({"default-currency": "AUD"}, data[0])

    def test_transaction_value(self):
        data = self.process([
            fac.TransactionFactory.build(value_amount=1000)
        ])
        self.assertField({"transaction-value": "1000"}, data[0])

    def test_iati_id(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__iati_identifier="GB-1-123")
        ])
        self.assertField({"iati-identifier": "GB-1-123"}, data[0])

    def test_hierarchy(self):
        activity = fac.ActivityFactory.build(
            hierarchy=1
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'hierarchy': "1"}, data[0])

    def test_last_updated_datetime(self):
        activity = fac.ActivityFactory.build(
            last_updated_datetime=datetime.date(2012, 1, 1)
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'last-updated-datetime': "2012-01-01"}, data[0])

    def test_default_language(self):
        activity = fac.ActivityFactory.build(
            default_language=cl.Language.english
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'default-language': "en"}, data[0])

    def test_reporting_org(self):
        activity = fac.ActivityFactory.build(
            reporting_org=fac.OrganisationFactory.build(name='rep',
                    ref='rep_ref', type=cl.OrganisationType.foundation),
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"reporting-org": "rep"}, data[0])
        self.assertField({"reporting-org-ref": "rep_ref"}, data[0])
        self.assertField({"reporting-org-type": "Foundation"}, data[0])

    def test_title(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__title="test title")
        ])
        self.assertField({"title": "test title"}, data[0])

    def test_description(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__description="test desc")
        ])
        self.assertField({"description": "test desc"}, data[0])

    def test_activity_status(self):
        activity = fac.ActivityFactory.build(
            activity_status=cl.ActivityStatus.pipelineidentification
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'activity-status-code': "1"}, data[0])

    def test_start_planned(self):
        activity = fac.ActivityFactory.build(
            start_planned=datetime.date(2011, 1, 1))
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"start-planned": "2011-01-01"}, data[0])

    def test_end_planned(self):
        activity = fac.ActivityFactory.build(
            end_planned=datetime.date(2012, 1, 2))
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"end-planned": "2012-01-02"}, data[0])
        
    def test_start_actual(self):
        activity = fac.ActivityFactory.build(
            start_actual=datetime.date(2012, 1, 3))
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"start-actual": "2012-01-03"}, data[0])

    def test_end_actual(self):
        activity = fac.ActivityFactory.build(
            end_actual=datetime.date(2012, 1, 4))
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"end-actual": "2012-01-04"}, data[0])

    def test_accountable_org(self):
        activity = fac.ActivityFactory.build(
            participating_orgs=[
                fac.ParticipationFactory.build(
                    organisation=fac.OrganisationFactory.build(name='acc', ref='acc_ref', type=cl.OrganisationType.foundation),
                    role=cl.OrganisationRole.accountable,

                ),
                fac.ParticipationFactory.build(
                    role=cl.OrganisationRole.funding),
                fac.ParticipationFactory.build(
                    role=cl.OrganisationRole.implementing),
            ]
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])

        self.assertField({"participating-org (Accountable)": "acc"}, data[0])
        self.assertField({"participating-org-ref (Accountable)": "acc_ref"}, data[0])
        self.assertField({"participating-org-type (Accountable)": "Foundation"}, data[0])

    def test_funding_org(self):
        activity = fac.ActivityFactory.build(
            participating_orgs=[
                fac.ParticipationFactory.build(
                    organisation=fac.OrganisationFactory.build(name='fund',
                        ref='fund_ref', type=cl.OrganisationType.foundation),
                    role=cl.OrganisationRole.funding),
            ]
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"participating-org (Funding)": "fund"}, data[0])
        self.assertField({"participating-org-ref (Funding)": "fund_ref"}, data[0])
        self.assertField({"participating-org-type (Funding)": "Foundation"}, data[0])

    def test_implementing_org(self):
        activity = fac.ActivityFactory.build(
            participating_orgs=[
                fac.ParticipationFactory.build(
                    organisation=fac.OrganisationFactory.build(name='impl',
                        ref="impl_ref", type=cl.OrganisationType.foundation),
                    role=cl.OrganisationRole.implementing),
            ]
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"participating-org (Implementing)": "impl"}, data[0])
        self.assertField({"participating-org-ref (Implementing)": "impl_ref"}, data[0])
        self.assertField({"participating-org-type (Implementing)": "Foundation"}, data[0])

    def test_extending_org(self):
        activity = fac.ActivityFactory.build(
            participating_orgs=[
                fac.ParticipationFactory.build(
                    organisation=fac.OrganisationFactory.build(name='ext',
                        ref="ext_ref", type=cl.OrganisationType.foundation),
                    role=cl.OrganisationRole.extending),
            ]
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({"participating-org (Extending)": "ext"}, data[0])
        self.assertField({"participating-org-ref (Extending)": "ext_ref"}, data[0])
        self.assertField({"participating-org-type (Extending)": "Foundation"}, data[0])

    def test_recipient_country_code(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia)
                    ])
            )
        ])
        self.assertField({"recipient-country-code": "ZM"}, data[0])

    def test_recipient_country(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia),
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.australia)
                    ])
            )
        ])
        self.assertField({"recipient-country": "Zambia;Australia"}, data[0])

    def test_recipient_country_percentage(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia,
                            percentage=20),
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.australia,
                            percentage=80)
                    ])
            )
        ])
        self.assertField({"recipient-country-percentage": "20;80"}, data[0])

    def test_recipient_country_percentage_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia)
                    ])
            )
        ])
        self.assertField({"recipient-country-percentage": ""}, data[0])

    def test_sector_code(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education)
                    ])
            )
        ])
        self.assertField({"sector-code": "11130;11220"}, data[0])

    def test_sector(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education)
                    ])
            )
        ])
        self.assertField(
            {"sector": "Teacher training;Primary education"},
            data[0])

    def test_sector_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(sector=None),
                    ])
            )
        ])
        self.assertField({"sector": ""}, data[0])

    def test_sector_percentage(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training,
                            percentage=60),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education,
                            percentage=40)
                    ])
            )
        ])
        self.assertField({"sector-percentage": "60;40"}, data[0])

    def test_sector_percentage_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training,
                            percentage=None),
                    ])
            )
        ])
        self.assertField({"sector-percentage": ""}, data[0])

    
    def test_default_finance_type(self):
        activity = fac.ActivityFactory.build(
            default_finance_type=cl.FinanceType.bank_bonds
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'default-finance-type-code': "810"}, data[0])

    def test_default_flow_type(self):
        activity = fac.ActivityFactory.build(
            default_flow_type=cl.FlowType.private_grants
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'default-flow-type-code': "30"}, data[0])

    def test_default_aid_type(self):
        activity = fac.ActivityFactory.build(
            default_aid_type=cl.AidType.debt_relief
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'default-aid-type-code': "F01"}, data[0])

    def test_default_tied_status(self):
        activity = fac.ActivityFactory.build(
            default_tied_status=cl.TiedStatus.tied
        )
        data = self.process([
            fac.TransactionFactory.build(activity=activity)
        ])
        self.assertField({'default-tied-status-code': "4"}, data[0])


class TestTransactionByCountry(TestCase, CSVTstMixin):
    def serialize(self, data):
        return serialize.csv_transaction_by_country(data)

    def example(self):
        ret = []
        act = example()
        for transaction in act.transactions:
            for country in act.recipient_country_percentages:
                ret.append((transaction, country))
        return ret

    def test_rec_country_code_0(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": "KE"}, data[0])

    def test_rec_country_code_1(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": "UG"}, data[1])

    def test_trans_date_0(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "2012-06-30"}, data[1])

    def test_trans_date_2(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "2012-09-30"}, data[2])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": "GB-1-123"}, data[2])


class TestTransactionBySector(TestCase, CSVTstMixin):
    def serialize(self, data):
        return serialize.csv_transaction_by_sector(data)

    def example(self):
        ret = []
        act = example()
        for transaction in act.transactions:
            for sector in act.sector_percentages:
                ret.append((transaction, sector))
        return ret

    def test_sector_code_0(self):
        data = self.process(self.example())
        self.assertField({"sector-code": "11130"}, data[0])

    def test_sector_code_1(self):
        data = self.process(self.example())
        self.assertField({"sector-code": "11220"}, data[1])

    def test_trans_date_0(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "2012-06-30"}, data[1])

    def test_trans_date_2(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "2012-09-30"}, data[2])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": "GB-1-123"}, data[2])

    def test_recepient_country_code(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": "KE;UG"}, data[0])

