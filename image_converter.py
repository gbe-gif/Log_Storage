from PySide6.QtGui import QImage, QPixmap

def pil_to_pixmap(image):
    """
    PIL.Image를 입력받아 RGBA 포맷의 QImage로 변환한 후,
    UI에 출력할 수 있는 QPixmap으로 변환하여 반환합니다.
    """
    # RGBA 원시 바이트 데이터 추출
    raw_data = image.tobytes("raw", "RGBA")
    
    # QImage 생성 (Format_RGBA8888 사용)
    qimg = QImage(raw_data, image.width, image.height, QImage.Format_RGBA8888)
    
    # QPixmap으로 변환
    pixmap = QPixmap.fromImage(qimg)
    
    return pixmap