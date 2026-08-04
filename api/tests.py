from unittest.mock import Mock, patch

from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase, override_settings
from rest_framework import status

from static.scripts.api_examples.example_api_client import (
    fetch_all_members,
    fetch_properties,
)


class ExampleApiClientTests(SimpleTestCase):
    @patch("static.scripts.api_examples.example_api_client.requests.get")
    def test_property_fetch_follows_all_pages(self, mock_get):
        first_response = Mock()
        first_response.json.return_value = {
            "results": [{"mcid": "MC1"}],
            "next": "https://example.test/api/dpcfam/mcs/?page=2",
        }
        second_response = Mock()
        second_response.json.return_value = {
            "results": [{"mcid": "MC10"}],
            "next": None,
        }
        mock_get.side_effect = [first_response, second_response]

        properties = fetch_properties(
            "https://example.test/api/",
            "dpcfam",
            ["MC1", "MC10"],
        )

        self.assertEqual(properties, [{"mcid": "MC1"}, {"mcid": "MC10"}])
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(
            mock_get.call_args_list[0].kwargs["params"],
            {"mcids": "MC1,MC10"},
        )
        self.assertIsNone(mock_get.call_args_list[1].kwargs["params"])

    @patch("static.scripts.api_examples.example_api_client.requests.get")
    def test_member_fetch_uses_largest_page_size_by_default(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "count": 1,
            "results": [{"protein_id": "P00001"}],
            "next": None,
        }
        mock_get.return_value = response

        members = fetch_all_members(
            "https://example.test/api/",
            "dpcfam",
            "MC1",
        )

        self.assertEqual(members, [{"protein_id": "P00001"}])
        self.assertEqual(
            mock_get.call_args.kwargs["params"],
            {"page_size": 500},
        )


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    SECURE_SSL_REDIRECT=False,
)
class ApiEndpointTests(TransactionTestCase):
    """Exercise the read-only API against small unmanaged-table fixtures."""

    tables = (
        "dpcfam_mcs_sequences",
        "dpcstruct_mcs_sequences",
        "dpcfam_mcs_properties",
        "dpcstruct_mcs_properties",
        "dpc_uniprot_proteins",
    )

    def setUp(self):
        super().setUp()
        self._drop_test_tables()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE dpc_uniprot_proteins (
                    protein_id varchar(50) PRIMARY KEY,
                    protein_length integer NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE dpcfam_mcs_properties (
                    mcid varchar(50) PRIMARY KEY,
                    size_uniref50 integer NOT NULL,
                    avg_len double precision,
                    std_avg_len double precision,
                    lc_percent double precision,
                    cc_percent double precision,
                    dis_percent double precision,
                    tm double precision,
                    pfam_da text,
                    da_percent double precision,
                    avg_ov_percent double precision,
                    overlap_label varchar(50)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE dpcfam_mcs_sequences (
                    id bigint PRIMARY KEY,
                    mcid varchar(50) NOT NULL,
                    protein_id varchar(50) NOT NULL,
                    seq_range varchar(100),
                    seq_length integer,
                    aa_seq text
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE dpcstruct_mcs_properties (
                    mc_id varchar(50) PRIMARY KEY,
                    mc_size integer NOT NULL,
                    len_aa double precision,
                    len_std double precision,
                    len_ratio double precision,
                    plddt double precision,
                    disorder double precision,
                    tmscore double precision,
                    lddt double precision,
                    pident double precision,
                    pfam_score double precision,
                    pfam_da text
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE dpcstruct_mcs_sequences (
                    id bigint PRIMARY KEY,
                    mc_id varchar(50) NOT NULL,
                    protein_id varchar(50) NOT NULL,
                    prot_range varchar(100),
                    prot_seq text
                )
                """
            )

            cursor.executemany(
                """
                INSERT INTO dpc_uniprot_proteins (protein_id, protein_length)
                VALUES (%s, %s)
                """,
                (("P00001", 100), ("P00002", 120), ("P00003", 140)),
            )
            cursor.executemany(
                """
                INSERT INTO dpcfam_mcs_properties (mcid, size_uniref50)
                VALUES (%s, %s)
                """,
                tuple((f"MC{number}", number) for number in range(1, 13)),
            )
            cursor.executemany(
                """
                INSERT INTO dpcfam_mcs_sequences (
                    id,
                    mcid,
                    protein_id,
                    seq_range,
                    seq_length,
                    aa_seq
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    (1, "MC1", "P00001", "1-20", 20, "A" * 20),
                    (2, "MC1", "P00002", "5-24", 20, "C" * 20),
                ),
            )
            cursor.executemany(
                """
                INSERT INTO dpcstruct_mcs_properties (mc_id, mc_size)
                VALUES (%s, %s)
                """,
                (("MC1", 2), ("MC2", 1)),
            )
            cursor.executemany(
                """
                INSERT INTO dpcstruct_mcs_sequences (
                    id,
                    mc_id,
                    protein_id,
                    prot_range,
                    prot_seq
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    (1, "MC1", "P00001", "1-20", "A" * 20),
                    (2, "MC1", "P00003", "10-29", "G" * 20),
                ),
            )

    def tearDown(self):
        self._drop_test_tables()
        super().tearDown()

    def _drop_test_tables(self):
        with connection.cursor() as cursor:
            for table in self.tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

    def test_api_root_lists_both_datasets(self):
        response = self.client.get("/api/?format=json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.json()),
            {"dpcfam/mcs", "dpcstruct/mcs"},
        )

    def test_dpcfam_list_is_paginated_and_naturally_sorted(self):
        response = self.client.get("/api/dpcfam/mcs/?format=json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["count"], 12)
        self.assertEqual(len(payload["results"]), 10)
        self.assertEqual(
            [item["mcid"] for item in payload["results"][:3]],
            ["MC1", "MC2", "MC3"],
        )
        self.assertIsNotNone(payload["next"])

    def test_dpcfam_filter_detail_and_members(self):
        filtered = self.client.get(
            "/api/dpcfam/mcs/?mcids=MC1,MC10&format=json"
        )
        detail = self.client.get("/api/dpcfam/mcs/MC1/?format=json")
        members = self.client.get(
            "/api/dpcfam/mcs/MC1/members/?page_size=1&format=json"
        )

        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.json()["count"], 2)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.json()["mcid"], "MC1")
        self.assertEqual(members.status_code, status.HTTP_200_OK)
        self.assertEqual(members.json()["count"], 2)
        self.assertEqual(len(members.json()["results"]), 1)
        self.assertIsNotNone(members.json()["next"])

    def test_dpcstruct_filter_detail_and_members(self):
        filtered = self.client.get(
            "/api/dpcstruct/mcs/?mcids=MC2&format=json"
        )
        detail = self.client.get("/api/dpcstruct/mcs/MC1/?format=json")
        members = self.client.get(
            "/api/dpcstruct/mcs/MC1/members/?page_size=500&format=json"
        )

        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.json()["count"], 1)
        self.assertEqual(filtered.json()["results"][0]["mc_id"], "MC2")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.json()["mc_id"], "MC1")
        self.assertEqual(members.status_code, status.HTTP_200_OK)
        self.assertEqual(members.json()["count"], 2)

    def test_api_is_read_only_and_unknown_ids_return_404(self):
        post_response = self.client.post(
            "/api/dpcfam/mcs/",
            data={"mcid": "MC99", "size_uniref50": 1},
        )
        missing_response = self.client.get(
            "/api/dpcfam/mcs/DOES-NOT-EXIST/?format=json"
        )

        self.assertEqual(
            post_response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            missing_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
