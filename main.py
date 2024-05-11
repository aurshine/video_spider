import whisper
from whisper.utils import get_writer


model = whisper.load_model("large")
result = model.transcribe("audio_.wav", language='zh')
writer = get_writer('srt', 'test')
print(result["text"])

writer(result, 'a.srt')