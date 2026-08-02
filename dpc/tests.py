from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import connection
from django.test import SimpleTestCase, TransactionTestCase, override_settings


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    SECURE_SSL_REDIRECT=False,
)
class BasicHttpTests(SimpleTestCase):
    def test_liveness_endpoint(self):
        response = self.client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @override_settings(DEBUG=False)
    def test_unknown_page_uses_production_404(self):
        response = self.client.get("/this-page-does-not-exist")

        self.assertEqual(response.status_code, 404)
        content = response.content.decode()
        self.assertNotIn("Using the URLconf", content)
        self.assertNotIn("DEBUG = True", content)

    def test_data_route_rejects_path_traversal(self):
        response = self.client.get("/data/../manage.py")

        self.assertEqual(response.status_code, 404)

    def test_data_route_serves_an_allowed_file(self):
        with TemporaryDirectory() as temporary_root:
            data_root = Path(temporary_root)
            allowed_file = data_root / "downloads" / "dpcfam" / "example.txt"
            allowed_file.parent.mkdir(parents=True)
            allowed_file.write_text("fixture\n")

            with self.settings(DPC_DATA_ROOT=data_root):
                response = self.client.get("/data/downloads/dpcfam/example.txt")
                response_content = b"".join(response.streaming_content)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_content, b"fixture\n")


@override_settings(
    ALLOWED_HOSTS=["testserver"],
    SECURE_SSL_REDIRECT=False,
)
class ReadinessTests(TransactionTestCase):
    scientific_tables = (
        "dpcfam_mcs_properties",
        "dpcstruct_mcs_properties",
    )

    required_directories = (
        "production_files/dpcfam/metaclusters_fasta",
        "production_files/dpcfam/metaclusters_hmms",
        "production_files/dpcfam/metaclusters_cdhit_msas",
        "production_files/dpcstruct/dpcstruct_reps_seqs",
        "production_files/dpcstruct/dpcstruct_reps_pdbs",
        "downloads/dpcfam",
        "downloads/dpcstruct",
    )

    def _drop_scientific_tables(self):
        with connection.cursor() as cursor:
            for table_name in self.scientific_tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    def tearDown(self):
        self._drop_scientific_tables()
        super().tearDown()

    def test_readiness_fails_closed_without_scientific_data(self):
        self._drop_scientific_tables()

        with TemporaryDirectory() as temporary_root:
            with self.settings(DPC_DATA_ROOT=Path(temporary_root)):
                response = self.client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "not_ready",
                "checks": {
                    "database": True,
                    "scientific_tables": False,
                    "data_files": False,
                },
            },
        )

    def test_readiness_succeeds_with_minimal_dependencies(self):
        self._drop_scientific_tables()

        with connection.cursor() as cursor:
            for table_name in self.scientific_tables:
                cursor.execute(f'CREATE TABLE "{table_name}" (id integer)')
                cursor.execute(f'INSERT INTO "{table_name}" (id) VALUES (1)')

        with TemporaryDirectory() as temporary_root:
            data_root = Path(temporary_root)

            for relative_directory in self.required_directories:
                directory = data_root / relative_directory
                directory.mkdir(parents=True)
                (directory / ".fixture").write_text("ready\n")

            with self.settings(DPC_DATA_ROOT=data_root):
                response = self.client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ready",
                "checks": {
                    "database": True,
                    "scientific_tables": True,
                    "data_files": True,
                },
            },
        )
