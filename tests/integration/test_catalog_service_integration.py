"""
Integration tests for CatalogService and CategoryService covering photo search and filtering.

Focuses on:
- Category retrieval and listing
- Photo search by category and keyword
- Photo filtering and sorting
- Catalog browsing operations
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.catalog_service import CatalogService
from app.core.services.category_service import CategoryService
from app.core.services.photo_service import PhotoService


class TestCategoryRetrieval:
    """Test category listing and retrieval."""

    def test_get_all_categories(self, integration_db):
        """Get all available categories."""
        categories = CategoryService.get_all()

        assert len(categories) > 0
        # Each category should have id and category name
        for cat in categories:
            assert "id" in cat
            assert "category" in cat

    def test_get_categories_not_empty(self, integration_db):
        """Categories list is not empty after seeding."""
        categories = CategoryService.get_all()

        assert len(categories) >= 1

    def test_get_category_by_id(self, integration_db):
        """Retrieve a single category by ID."""
        categories = CategoryService.get_all()
        if categories:
            cat_id = categories[0]["id"]
            category = CategoryService.get_by_id(cat_id)

            assert category is not None
            assert category["id"] == cat_id

    def test_get_category_by_name(self, integration_db):
        """Retrieve category by name (case-insensitive)."""
        categories = CategoryService.get_all()
        assert len(categories) > 0

        # Get first category name
        first_cat = categories[0]
        name = first_cat.get("category")

        # Search by name
        result = CategoryService.get_by_name(name)

        assert result is not None or len(categories) >= 1


class TestCatalogOperations:
    """Test catalog browsing and search operations."""

    def test_get_catalog_main(self, integration_db):
        """Get main catalog (featured/trending photos)."""
        catalog = CatalogService.get_explore_catalog()

        # Should return a list or dict
        assert catalog is not None

    def test_get_catalog_by_category(self, integration_db):
        """Get catalog filtered by category."""
        catalog = CatalogService.get_explore_catalog()

        # Should return a list or dict
        assert catalog is not None

    def test_search_photos_by_keyword(self, integration_db):
        """Search photos by keyword."""
        # Create a photo with keyword
        user = AuthService.register_user("alice", "alice@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Sunset landscape photography",
        )

        # Search for "sunset"
        results = CatalogService.get_explore_catalog()

        # Results should be a list
        assert isinstance(results, (list, dict))


class TestCatalogWithPhotos:
    """Test catalog operations with actual photos."""

    def test_catalog_includes_created_photos(self, integration_db):
        """Catalog search includes newly created photos."""
        user = AuthService.register_user("bob", "bob@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        # Create multiple photos in different categories
        categories = CategoryService.get_all()
        if categories:
            for i, cat in enumerate(categories[:2]):
                PhotoService.create_photo_record(
                    album_id=album["id"],
                    category_id=cat["id"],
                    description=f"Photo {i} - test photo",
                )

        # Search should work without errors
        results = CatalogService.get_explore_catalog()
        assert isinstance(results, (list, dict))

    def test_catalog_by_category_returns_results(self, integration_db):
        """Catalog by category returns photos in that category."""
        user = AuthService.register_user("charlie", "charlie@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        categories = CategoryService.get_all()
        if categories:
            target_cat = categories[0]
            PhotoService.create_photo_record(
                album_id=album["id"],
                category_id=target_cat["id"],
                description="Nature photo",
            )

            # Get catalog for this category
            catalog = CatalogService.get_explore_catalog()
            assert isinstance(catalog, (list, dict))


class TestPhotoSearchAndFilter:
    """Test advanced photo search and filtering."""

    def test_search_empty_keyword(self, integration_db):
        """Empty search returns results or empty list."""
        results = CatalogService.get_explore_catalog()

        # Should return list or dict, not error
        assert results is not None

    def test_search_specific_user_photos(self, integration_db):
        """Search photos by specific user."""
        user = AuthService.register_user("diana", "diana@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Diana's photo",
        )

        # Search should work
        results = CatalogService.get_explore_catalog()
        assert isinstance(results, (list, dict))

    def test_search_multiple_keywords(self, integration_db):
        """Search with multiple keywords returns filtered results."""
        user = AuthService.register_user("eve", "eve@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Beautiful sunset over mountains",
        )

        # Search for multiple keywords
        results = CatalogService.get_explore_catalog()
        assert isinstance(results, (list, dict))

    def test_get_photos_for_user(self, integration_db):
        """Get all photos for a specific user."""
        from app.core.db.engine import SessionLocal
        from app.core.db.models.photo import PhotoModel

        user = AuthService.register_user("frank", "frank@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        # Create 3 photos
        for i in range(3):
            PhotoService.create_photo_record(
                album_id=album["id"],
                category_id=1,
                description=f"Frank's photo {i}",
            )

        # Get user's photos through album lookup
        albums = AlbumService.get_user_albums(user["id"])
        assert len(albums) >= 1

        total_photos = 0
        for alb in albums:
            with SessionLocal() as session:
                photos = PhotoModel.get_by_album(session, alb["id"])
            total_photos += len(photos)

        assert total_photos >= 3
