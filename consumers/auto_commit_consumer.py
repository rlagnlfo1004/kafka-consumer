import json
import pandas as pd
from confluent_kafka import Consumer, KafkaException

from base_consumer import BaseConsumer


class AutoCommitConsumer(BaseConsumer):
    def __init__(self, group_id):
        super().__init__(group_id)
        self.topics = ['apis.seouldata.rt-bicycle']

        conf = {'bootstrap.servers': self.BOOTSTRAP_SERVERS,
                'group.id': self.group_id,
                'auto.offset.reset': 'lastest',
                'enable.auto.commit': 'true',
                'auto.commit.interval.ms': 6000  # default : 5000(5초)
                }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(self.topics, on_assign=self.callback_on_assign)


    def poll(self):
        try:
            while True:
                msg_list = self.consumer.consume(num_messages=100)
                if msg_list is None or len(msg_list) == 0: continue

                self.logger.info(f'message count:{len(msg_list)}')
                for msg in msg_list:
                    error = msg.error()
                    if error:
                        self.handle_error(msg, error)

                # 로직 처리 부분
                # Kafka 레코드에 대한 전처리, Target Sink 등 수행
                self.logger.info(f'message 처리 로직 시작')
                msg_val_list = [json.loads(msg.value().decode('utf-8')) for msg in msg_list]
                df = pd.DataFrame(msg_val_list)
                print(df[:10])

        except KafkaException as e:
            self.logger.exception("Kafka exception occurred during message consumption")
        except KeyboardInterrupt:  # Ctrl + C 눌러 종료시
            self.logger.info("Shutting down consumer due to keyboard interrupt.")

        finally:
            self.consumer.close()
            self.logger.info("Consumer closed.")

if __name__ == '__main__':
    auto_commit_consumer = AutoCommitConsumer('auto_commit_consumer')
    auto_commit_consumer.poll()