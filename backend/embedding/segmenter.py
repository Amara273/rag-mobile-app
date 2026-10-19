from khmerns import KhmerSegmenter, tokenize, normalize

TEXT = 'សួស្តីបងប្អូនកម្ពុជា។'

segmenter = KhmerSegmenter()

res = tokenize(normalize(TEXT))

print(res)