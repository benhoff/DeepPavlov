# Copyright 2017 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from deeppavlov.core.common.registry import register
from deeppavlov.core.models.component import Component
from deeppavlov.core.commands.utils import expand_path
from logging import getLogger

from bert_dp.preprocessing import convert_examples_to_features, InputExample
from bert_dp.tokenization import FullTokenizer

logger = getLogger(__name__)


@register('bert_split_preprocessor')
class BertSplitPreprocessor(Component):
    # TODO: docs

    def __init__(self, vocab_file, do_lower_case=True, max_seq_length: int = 512, *args, **kwargs):
        self.max_seq_length = max_seq_length
        vocab_file = str(expand_path(vocab_file))
        self.tokenizer = FullTokenizer(vocab_file=vocab_file, do_lower_case=do_lower_case)

    def __call__(self, samples):
        texts = []
        for i in range(len(samples[0])):
            t = []
            for el in samples:
                t.append(el[i])
            texts.append(t)
        texts_a = texts[0]
        texts_b = [None] * len(texts[0])
        # TODO: add unique id
        example_a = [InputExample(unique_id=0, text_a=text_a, text_b=text_b) for text_a, text_b in zip(texts_a, texts_b)]
        examples = []
        for t in texts[1:]:
            ex = [InputExample(unique_id=0, text_a=text_a, text_b=text_b) for text_a, text_b in
                  zip(t, texts_b)]
            examples.append(ex)
        feature_a = convert_examples_to_features(example_a, self.max_seq_length, self.tokenizer)
        features = [convert_examples_to_features(el, self.max_seq_length, self.tokenizer) for el in examples]
        split_features = []
        for f in features:
            split_features.append([InputSplitFeatures(*el) for el in zip(feature_a, f)])

        return split_features

class InputSplitFeatures(object):
  """A single set of features of data."""

  def __init__(self, feature_a, feature_b):
    self.unique_id = feature_a.unique_id
    self.tokens_a = feature_a.tokens
    self.input_ids_a = feature_a.input_ids
    self.input_mask_a = feature_a.input_mask
    self.input_type_ids_a = feature_a.input_type_ids
    self.tokens_b = feature_b.tokens
    self.input_ids_b = feature_b.input_ids
    self.input_mask_b = feature_b.input_mask
    self.input_type_ids_b = feature_b.input_type_ids
