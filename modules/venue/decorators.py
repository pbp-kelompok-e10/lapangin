from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest # Impor HttpRequest jika Anda menggunakan typing


def is_venue_provider_or_admin(user) -> bool:
    """
    Memeriksa apakah pengguna adalah Admin (is_staff) atau memiliki
    atribut is_venue_provider (Pemilik Lapangan).
    """
    # Pastikan user sudah login sebelum melakukan pemeriksaan
    if not user.is_authenticated:
        return False
        
    # Cek apakah dia Staff/Admin ATAU Pemilik Lapangan
    is_provider = getattr(user, 'is_venue_provider', False)
    
    return user.is_staff or is_provider


def venue_access_required(view_func):
    """
    Decorator untuk membatasi akses ke views hanya untuk Admin/Staff atau 
    Venue Provider. Mengarahkan ke halaman login jika gagal.
    """
    def check_access(user):
        return is_venue_provider_or_admin(user)
    
    # Gunakan user_passes_test bawaan Django
    decorated_view = user_passes_test(
        check_access,
        login_url='/login/' # Ganti dengan URL login yang sesuai di proyek Anda
    )(view_func)
    
    # Tambahkan pesan error custom jika otorisasi gagal setelah login
    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not is_venue_provider_or_admin(request.user):
            # Jika user terotentikasi tapi tidak punya role yang sesuai
            messages.error(request, 'Anda tidak memiliki izin untuk mengelola Venue.')
            return redirect('venue:search_venue') # Redirect ke halaman pencarian umum
            
        return decorated_view(request, *args, **kwargs)

    return _wrapped_view