import os
import base64
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image
try:
    import win32gui
    import win32ui
    import win32con
    import pythoncom
except ImportError:
    # Fallback for development on non-windows
    win32gui = None

from loguru import logger

class ScreenshotService:
    """
    Service for capturing screenshots of SAP GUI windows and controls.
    """
    
    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        Captures the full window content for the given HWND.
        """
        if not win32gui:
            logger.warning("win32gui not available. Screenshot capture skipped.")
            return None
            
        try:
            # Get window dimensions
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bot - top

            # Create device contexts
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Copy window into bitmap
            result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return img
        except Exception as e:
            logger.error(f"Failed to capture window {hwnd}: {str(e)}")
            return None

    def capture_area(self, window_img: Image.Image, bounds: Tuple[int, int, int, int]) -> Image.Image:
        """
        Crops a window image to the specified control bounds (left, top, width, height).
        """
        left, top, width, height = bounds
        return window_img.crop((left, top, left + width, top + height))

    def to_base64(self, img: Image.Image, format: str = "PNG") -> str:
        """
        Converts an Image object to a base64 string.
        """
        buffered = BytesIO()
        img.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def save_to_file(self, img: Image.Image, path: str):
        """
        Saves the image to the specified path.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
