import basetest

class TestBackend(basetest.BaseTest, object):
    def test_init(self):
        import matplotlib
        import mplgui

        self.assertEqual(matplotlib.get_backend(), 'module://mplgui.lib.backend')

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        
        self.assertIs(type(fig.canvas), mplgui.lib.backend.FigureCanvas)
        
        if __name__ == '__main__':
            plt.show()
        plt.close('all')

    def test_undo_history(self):
        import matplotlib.pyplot as plt
        import mplgui

        fig, ax = plt.subplots()

        mplgui.undo_history(5)
        self.assertEqual(fig.canvas._undo_history, 5)
        fig.canvas.record_change()
        fig.canvas.record_change()
        fig.canvas.record_change()
        self.assertEqual(len(fig.canvas._states), 3)
        fig.canvas.record_change()
        fig.canvas.record_change()
        self.assertEqual(len(fig.canvas._states), 5)
        fig.canvas.record_change()
        self.assertEqual(len(fig.canvas._states), 5)

        mplgui.undo_history(3)
        self.assertEqual(len(fig.canvas._states), 3)

        mplgui.undo_history(-1)
        self.assertEqual(fig.canvas._undo_history, 0)
        self.assertEqual(len(fig.canvas._states), 1)

        mplgui.undo_history(1)
        self.assertEqual(fig.canvas._undo_history, 1)
        self.assertEqual(len(fig.canvas._states), 1)

        mplgui.undo_history(100)
        self.assertEqual(len(fig.canvas._states), 1)
        
if __name__ == '__main__':
    import unittest
    unittest.main(failfast = True)
