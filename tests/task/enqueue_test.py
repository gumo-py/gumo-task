from gumo.task.application import enqueue


def test_enqueue():
    print('test')

    enqueue(url='/task')
