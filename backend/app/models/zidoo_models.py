from pydantic import BaseModel
from typing import Optional, Dict, Any

class VideoInfo(BaseModel):
    status: int
    title: str
    path: str
    currentPosition: int
    duration: int
    width: int
    height: int
    fps: float
    formt: str
    filesize: str
    bitrate: str
    output: str
    subtitleInfo: str
    audioInfo: str

class SubtitleInfo(BaseModel):
    index: int
    information: str

class AudioInfo(BaseModel):
    index: int
    information: str

class PlayModeInfo(BaseModel):
    index: int
    information: str

class ZoomInfo(BaseModel):
    index: int
    information: str

class ThreeDInfo(BaseModel):
    index: int
    information: str
    isMvc3D: bool

class ZidooPlayStatus(BaseModel):
    status: int
    msg: Optional[str] = None
    video: Optional[VideoInfo] = None
    subtitle: Optional[SubtitleInfo] = None
    audio: Optional[AudioInfo] = None
    playMode: Optional[PlayModeInfo] = None
    zoom: Optional[ZoomInfo] = None
    threeD: Optional[ThreeDInfo] = None

class NotificationPayload(BaseModel):
    file_path: str

class ToggleServiceRequest(BaseModel):
    serviceName: str
    action: str  # "start" or "stop"

class ToggleServiceResponse(BaseModel):
    success: bool
    message: str
    service_status: str 