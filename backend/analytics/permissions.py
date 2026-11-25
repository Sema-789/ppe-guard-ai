from rest_framework import permissions


class IsHSEOrAdmin(permissions.BasePermission):
    """Yalnız HSE mütəxəssisi və ya Admin dəyişiklik/təsdiq edə bilsin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return getattr(request.user, "role", None) in ("hse", "admin")


class IsAdminOnly(permissions.BasePermission):
    """Yalnız Admin silmə və kritik idarəetmə əməliyyatları edə bilsin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return getattr(request.user, "role", None) == "admin"