from cloudAMQP_client import CloudAMQPClient

CloudAMQP_URL = "amqp://vyqtbzjg:0_b7POsAe_aSbjmVrNgbVLBOv18fQERf@wombat.rmq.cloudamqp.com/vyqtbzjg"
TEST_QUEUE_NAME = "test"

def test_basic():
  client = CloudAMQPClient(CloudAMQP_URL,TEST_QUEUE_NAME )

  sentMsg = {"test":"test"}
  client.sendMessage(sentMsg)

  client.sleep(5)

  reveivedMsg = client.getMessage()

  assert sentMsg == reveivedMsg
  print("test_basic passed!")

if __name__ == "__main__":
  test_basic()