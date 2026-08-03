# DPCexplorer API Implementation

This document explains how the DPCexplorer REST API was built with Django REST Framework (DRF). It is written for anyone who wants to understand the API from scratch, reproduce it in a similar project, or extend it later. Section 1 gives a general overview of how DRF works. Section 2 walks through the actual implementation used in DPCexplorer, file by file.

## Section 1: Django REST Framework Overview

Django REST Framework is a toolkit built on top of Django that turns existing models into a web API, without changing how the underlying database or the rest of the Django project works. It adds a small number of building blocks, each with one clear job.

`serializers.py` is where the translation between Python objects and JSON happens. A serializer declares which fields of a model should be exposed to the outside world, in which format, and under which name. It also validates incoming data when the API accepts writes, although in a read-only API like DPCexplorer's, this direction is not used.

`views.py` is where the actual request handling logic lives. In DRF, a view (often a `ViewSet`) receives an HTTP request, decides which objects to fetch from the database, applies filtering or pagination if needed, and hands the result to a serializer to be converted into JSON. This is also where custom behavior, such as extra endpoints or renamed labels in the browsable API, gets added.

`urls.py` connects URLs to views. DRF ships with routers, most commonly `DefaultRouter`, which can generate a full set of URL patterns automatically from a single `ViewSet` registration: list, detail, and any custom actions. This avoids writing repetitive URL patterns by hand for every endpoint.

`settings.py` is where DRF is switched on for the project and where its global behavior is configured: default permissions (who can access the API), default authentication method, default pagination style, and so on. These defaults apply everywhere unless a specific view overrides them.

Together, these four pieces are enough to expose an existing database as a browsable, machine-readable API, with very little code, as long as the underlying Django models already exist.

## Section 2: DPCexplorer API Implementation

This is how the API was actually implemented in the DPCexplorer project, step by step.

### Step 1: Install Django REST Framework

```bash
pip install djangorestframework
```

### Step 2: Register the app in settings.py

`djangorestframework` was added to `INSTALLED_APPS`, alongside a new `api` app that would hold all the API-specific code:

```python
INSTALLED_APPS = [
    ...
    "rest_framework",
    'api',
]
```

### Step 3: Create the api app

```bash
django-admin startapp api
```

This generated the usual Django app skeleton. `apps.py` was left mostly untouched, apart from setting a clearer `verbose_name`:

```python
class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'DPCexplorer REST API'
```

This label is what shows up in the Django admin app list, so it was worth a small edit to make it self-explanatory.

### Step 4: serializers.py

The serializers describe how the existing, `managed=False` scientific models (`DpcfamMcsProperty`, `DpcfamMcsSequence`, `DpcStructMcsProperty`, `DpcStructMcsSequence`) get turned into JSON. Nothing here touches the database schema; each serializer just lists which fields to expose. Two serializers were written per dataset: one for the metacluster's properties (`DpcfamMcsPropertySerializer`, `DpcStructMcsPropertySerializer`), and one for its individual member sequences (`DpcfamMcsMemberSerializer`, `DpcStructMcsMemberSerializer`). The member serializers use a small trick worth noting: `protein_id` is not a direct field on the sequence model, it lives on a related `DpcUniprotProtein` object reached through a ForeignKey. Declaring it as `serializers.CharField(source='protein.protein_id', read_only=True)` lets the client receive a plain UniProt accession string directly, instead of a nested object it would then have to unpack.

### Step 5: views.py

Each dataset (DPCfam and DPCstruct) got its own `ViewSet`, built on DRF's `ReadOnlyModelViewSet`. This choice mirrors a decision already made elsewhere in the project: the API, like the Django admin panel, only ever reads the database, so a read-only base class rules out accidental writes through a public endpoint from the start. Each `ViewSet` supports an optional `?mcids=MC1,MC3,MC15` query parameter on its list endpoint, parsed by a small helper function, so a user can request a specific set of metaclusters instead of paging through all of them. A metacluster's member sequences are exposed through a separate `/members/` action rather than being nested inside the metacluster's own JSON, because a single DPCfam metacluster can hold well over 100,000 seed sequences: embedding them all would make ordinary responses unreasonably large. This `/members/` endpoint has its own pagination class, `MembersPagination`, distinct from the list endpoint's pagination, since the two deal with very different result sizes. Finally, a small `NamedViewSetMixin` overrides `get_view_name()` so that the browsable API shows readable, resource-specific titles, such as "DPCfam Metacluster MC1 - Members", instead of DRF's default mechanical naming derived from the Python class name.

### Step 6: urls.py

A single `DefaultRouter` was used to register both `ViewSet`s and generate all their URL patterns automatically. The one addition here is `DPCexplorerAPIRootView`, a small subclass of DRF's `APIRootView` that overrides `get_view_name()` and `get_view_description()`. By default, DRF derives the root page's title and description from the `APIRootView` class name and docstring, which produces a generic, uninformative label. Subclassing it and pointing a custom router (`DPCexplorerRouter`) at that subclass was enough to give the API root page a proper title, "DPCexplorer REST API - Django Framework", instead of the generic one. This is the same idea already applied to the Django admin site header elsewhere in the project, just applied to the DRF root view instead.

### Step 7: settings.py, permissions and pagination

The `REST_FRAMEWORK` dictionary in `settings.py` sets the defaults for the whole API:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}
```

The API is public and read-only, so it made no sense to require authentication for it: the same data is already public through the regular web pages. `AllowAny` and an empty authentication list reflect that on purpose, rather than by oversight.

### Step 8: endpoints

Once wired together, the API exposes the following endpoints:

```
GET /api/dpcfam/mcs/
GET /api/dpcfam/mcs/?mcids=MC1,MC3,MC15
GET /api/dpcfam/mcs/{mcid}/
GET /api/dpcfam/mcs/{mcid}/members/

GET /api/dpcstruct/mcs/
GET /api/dpcstruct/mcs/?mcids=MC1,MC5
GET /api/dpcstruct/mcs/{mc_id}/
GET /api/dpcstruct/mcs/{mc_id}/members/
```

### Extending the API

Anyone who wants to add a new dataset later should follow the same pattern: write a serializer for its properties and, if relevant, one for its members; write a `ReadOnlyModelViewSet` (reusing `NamedViewSetMixin` for consistent titles); register it on the existing router in `urls.py`. No changes to `settings.py` should be needed, since the global permission and pagination defaults already apply to any new `ViewSet`.
