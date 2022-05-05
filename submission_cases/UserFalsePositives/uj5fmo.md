 I have a window that has a list of buttons. When the buttons exceed the height of the window, I want to be able to scroll up and down, but the scroll bar moves and the buttons stay at their position. I found a SO solution, and I am not sure if it applies to my problem. Please let me know if it will work or if I have to fix it some other way.   


    # main.py
    
    from os import listdir
    from user32 import *
    from button import Button
    from pathlib import Path
    
    hInst = windll.kernel32.GetModuleHandleW(0)
    
    BTN_WIDTH = 300
    BTN_HEIGHT = 100
    
    def window_proc(hwnd: HWND, umsg: UINT, wparam: WPARAM, lparam: LPARAM) -> LRESULT:
        match umsg:
            case WindowMessage.CREATE:
                create_list_of_buttons(get_files(), hwnd)
            case WindowMessage.DESTROY:
                PostQuitMessage(0)
                return 0
            case WindowMessage.COMMAND:
                match wparam:
                    case 100:
                        print("hello")
        return DefWindowProcW(hwnd, umsg, wparam, lparam)
    
    
    def create_window(className, windowName):
        wnd_main = CreateWindowExW(
            0,
            className,
            windowName,
            WindowStyles.OVERLAPPED
            | WindowStyles.CAPTION
            | WindowStyles.SYSMENU
            | WindowStyles.THICKFRAME
            | WindowStyles.MINIMIZEBOX
            | WindowStyles.MAXIMIZEBOX
            | WindowStyles.CAPTION
            | WindowStyles.VSCROLL,
            CW_USEDEFAULT,
            CW_USEDEFAULT,
            600,
            600,
            0,
            0,
            hInst,
            0,
        )
        if not wnd_main:
            print("Window Creation Falid: ", GetLastError())
            return
        return wnd_main
    
    
    def get_files():
        folder_path = Path(__file__).parent / "log"
        return [file for file in listdir(folder_path) if file.endswith(".txt")]
    
    def create_list_of_buttons(filenames: list[str], parent_window):
        """
        Makes a list of button that have the file's name as their heading
        """
        x, y = 0, 0
        for button_id, filename in enumerate(filenames, 100):
            Button(filename, x, y, BTN_WIDTH, BTN_HEIGHT, parent_window, button_id).create_button()
            y += BTN_HEIGHT
    
    
    
    
    
    def main():
        wclassName = ctypes.c_wchar_p("My")
        wname = ctypes.c_wchar_p("Left")
        wndClass = WNDCLASSEXW()
        wndClass.cbSize = sizeof(WNDCLASSEXW)
        wndClass.style = ClassStyles.HREDRAW | ClassStyles.VREDRAW
        wndClass.lpfnWndProc = WNDPROC(window_proc)
        wndClass.cbClsExtra = 0
        wndClass.cbWndExtra = 0
        wndClass.hInstance = hInst
        wndClass.hIcon = 0
        wndClass.hCursor = 0
        wndClass.hBrush = windll.gdi32.GetStockObject(0)
        wndClass.lpszMenuName = 0
        wndClass.lpszClassName = wclassName
        wndClass.hIconSm = 0
    
        RegisterClassExW(byref(wndClass))
    
        wnd_main = create_window(wclassName, wname)
        ShowWindow(wnd_main, 5)
        UpdateWindow(wnd_main)
    
        msg = MSG()
        lpmsg = pointer(msg)
    
        while (GetMessageW(lpmsg, 0, 0, 0)) != 0:
            TranslateMessage(lpmsg)
            DispatchMessageW(lpmsg)
    
    
    main()
