import mytest




def test_enqueue():
    from gumo.task.application import enqueue
    print('test')

    enqueue(
        url='/task'
    )
