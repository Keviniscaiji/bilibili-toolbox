# -*- coding: utf-8 -*-
import wx
import win32api
import sys, os
import time
import threading

APP_TITLE = 'Bilibili Toodbox'
APP_ICON = '...'
class main(wx.Frame):
    def __init__(self, Toolbox):
        '''def'''
        wx.Frame.__init__(self, Toolbox,-1, APP_TITLE)
        self.SetBackgroundColour(wx.Colour(0,255,255))
        self.SetSize((500, 200))
        self.Center()

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
            exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
            icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
        else:
            icon = wx.Icon(APP_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        wx.StaticText(self, -1, 'please enter：', pos=(10, 50), size=(100, -1), style=wx.ALIGN_RIGHT)
        wx.StaticText(self, -1, 'please enter：', pos=(10, 80), size=(100, -1), style=wx.ALIGN_RIGHT)
        self.tip = wx.StaticText(self, -1, u'', pos=(145, 110), size=(150, -1), style=wx.ST_NO_AUTORESIZE)

        self.tc1 = wx.TextCtrl(self, -1, '', pos=(145, 50), size=(150, -1), name='TC01', style=wx.TE_AUTO_URL | wx.ALIGN_RIGHT)
        self.tc2 = wx.TextCtrl(self, -1, '', pos=(145, 80), size=(150, -1), name='TC02', style=wx.TE_PASSWORD | wx.ALIGN_RIGHT)

        btn_mea = wx.Button(self, -1, 'left click', pos=(300, 50), size=(150, 25))
        btn_meb = wx.Button(self, -1, 'mouse movement', pos=(300, 80), size=(150, 25))
        btn_close = wx.Button(self, -1, 'close', pos=(300, 110), size=(150, 25))

        self.tc1.Bind(wx.EVT_TEXT, self.EvtText)
        self.tc2.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_BUTTON, self.OnClose, btn_close)

        # mouse movement event
        btn_mea.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        btn_mea.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        btn_mea.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        btn_meb.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        # keyboard event
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # system interrupt
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # self.Bind(wx.EVT_PAINT, self.On_paint)
        # self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)

    def EvtText(self, evt):
        '''enter text event'''
        obj = evt.GetEventObject()
        objName = obj.GetName()
        text = evt.GetString()

        if objName == 'TC01':
            self.tc2.SetValue(text)
        elif objName == 'TC02':
            self.tc1.SetValue(text)

    def OnSize(self, evt):
        '''change the window size'''
        self.Refresh()
        evt.Skip()

    def OnClose(self, evt):
        #window close
        dlg = wx.MessageDialog(None, 'are u sure to close?', 'Just for reminding', wx.YES_NO | wx.ICON_QUESTION)
        if (dlg.ShowModal() == wx.ID_YES):
            self.Destroy()

    def OnLeftDown(self, evt):
        '''left click '''
        self.tip.SetLabel('left click')

    def OnLeftUp(self, evt):
        self.tip.SetLabel('bounce')

    def OnMouseWheel(self, evt):
        '''wheel rotation'''
        wheel = evt.GetWheelRotation()
        self.tip.SetLabel(str(wheel))

    def OnMouse(self, evt):
        '''mouse event'''
        self.tip.SetLabel(str(evt.EventType))

    def OnKeyDown(self, evt):
        '''keyboard event'''
        key = evt.GetKeyCode()
        self.tip.SetLabel(str(key))

class mainApp(wx.App):
    def OnInit(self):
        self.SetAppName(APP_TITLE)
        self.Frame = main(None)
        self.Frame.Show()
        return True

if __name__ == "__main__":
    app = mainApp()
    app.MainLoop()
