---
frameworks:
- 其他
license: Apache License 2.0
tasks:
- keyword-spotting
---

This is a custom wake-word model for Sherpa, trained on the GigaSpeech XL dataset (10,000 hours). It uses BPE modeling units, has a model size of approximately 3.3 MB, and employs the Zipformer architecture. Trained using Icefall and converted to ONNX format, the model is primarily designed for use with the Sherpa-ONNX inference engine.

Architecturally, it is a Zipformer model—essentially a highly compact automatic speech recognition (ASR) model—modified and constrained at the decoding stage to support wake-word functionality. It supports an unlimited number of custom wake-words, though performance tuning requires adjusting parameters for each specific wake-word.

#### Clone with HTTP
```bash
 git clone https://www.modelscope.cn/pkufool/sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01.git
```
