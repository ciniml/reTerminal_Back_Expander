from __future__ import division
import pcbnew

import FootprintWizardBase
import PadArray as PA


class SignalPadGridArray(PA.PadGridArray):
    def __init__(self, *args, **kwargs):
        super(SignalPadGridArray, self).__init__(*args, **kwargs)

    def NamingFunction(self, x, y):
        return str(y * self.nx + x + 1)

class PowerPthGridArray(PA.PadGridArray):
    def __init__(self, *args, **kwargs):
        super(PowerPthGridArray, self).__init__(*args, **kwargs)

    def NamingFunction(self, x, y):
        return "Power" + str(y * self.nx + x + 1)


class FixPinGridArray(PA.PadGridArray):
    def __init__(self, *args, **kwargs):
        super(FixPinGridArray, self).__init__(*args, **kwargs)

    def NamingFunction(self, x, y):
        return "~"


class HiroseFX23Wizard(FootprintWizardBase.FootprintWizard):
    pin_count_key = 'pin count'
    

    body_height_mm = 7.6
    body_width_offset_mm = (17.2-4.5)/2
    pad_outer_height_mm = 8.2
    pad_inner_height_mm = 4.4
    pad_length_mm = (pad_outer_height_mm - pad_inner_height_mm) / 2
    pad_width_mm = 0.3
    pad_pitch_mm = 0.5
    power_pin_pad_size_mm = 1.6
    power_pin_drill_size_mm = 1.2
    power_pin_offset_x_mm = (9.5 - 4.5)/2
    power_pin_center_y_mm = 6.1/2
    fix_pin_pad_size_mm = 1.4
    fix_pin_drill_size_mm = 1.0
    fix_pin_offset_x_mm = (15.7 - 4.5)/2
    fix_pin_center_y_mm = 2.6/2
    
    def GetName(self):
        return "Hirose_FX23"

    def GetDescription(self):
        return "Hirose FX23 Board to Board footprint"

    def GetValue(self):
        pin_count = self.parameters["Pins"][self.pin_count_key]
        return "FX23-%dS" % (pin_count,)

    def CheckParameters(self):
        self.CheckParam("Pins", self.pin_count_key, multiple=2, info='Pads must be multiple of 2')

    def GenerateParameterList(self):
        self.AddParam("Pins", self.pin_count_key, self.uInteger, 100)

    def GetPad(self):
        pad_width = pcbnew.FromMM(self.pad_width_mm)
        pad_length = pcbnew.FromMM(self.pad_length_mm)

        return PA.PadMaker(self.module).SMDPad(
            pad_length, pad_width, shape=pcbnew.PAD_SHAPE_RECT)

    def BuildThisFootprint(self):
        pins = self.parameters["Pins"]
        number_of_pins = pins[self.pin_count_key]
        pads_per_row = number_of_pins//2
        number_of_rows = 2
        pad_pitch = pcbnew.FromMM(self.pad_pitch_mm)
        row_pitch = pcbnew.FromMM((self.pad_inner_height_mm + self.pad_outer_height_mm)/2)
        pad_width = pcbnew.FromMM(self.pad_width_mm)
        pad_length = pcbnew.FromMM(self.pad_length_mm)
        power_pitch = pcbnew.FromMM(self.power_pin_offset_x_mm + self.pad_pitch_mm*(pads_per_row-1)/2)*2
        power_row_pitch = pcbnew.FromMM(self.power_pin_center_y_mm)*2
        fix_pin_pitch = pcbnew.FromMM(self.fix_pin_offset_x_mm + self.pad_pitch_mm*(pads_per_row-1)/2)*2
        fix_pin_row_pitch = pcbnew.FromMM(self.fix_pin_center_y_mm)*2

        # signal pin pad
        signal_pad = PA.PadMaker(self.module).SMDPad(pad_length, pad_width, shape=pcbnew.PAD_SHAPE_RECT)
        signal_array = SignalPadGridArray(signal_pad, pads_per_row, number_of_rows, pad_pitch, row_pitch)
        signal_array.AddPadsToModule(self.draw)

        # power PTH
        power_pth_drill = pcbnew.FromMM(self.power_pin_drill_size_mm)
        power_pth_size = pcbnew.FromMM(self.power_pin_pad_size_mm)
        power_pth = PA.PadMaker(self.module).THPad(power_pth_size, power_pth_size, power_pth_drill, shape=pcbnew.PAD_SHAPE_CIRCLE)
        power_array = PowerPthGridArray(power_pth, 2, 2, power_pitch, power_row_pitch)
        power_array.AddPadsToModule(self.draw)

        # fix pin PTH
        fix_pin_pth_drill = pcbnew.FromMM(self.fix_pin_drill_size_mm)
        fix_pin_pth_size = pcbnew.FromMM(self.fix_pin_pad_size_mm)
        fix_pin_pth = PA.PadMaker(self.module).THPad(fix_pin_pth_size, fix_pin_pth_size, fix_pin_pth_drill, shape=pcbnew.PAD_SHAPE_CIRCLE)
        fix_pin_array = FixPinGridArray(fix_pin_pth, 2, 2, fix_pin_pitch, fix_pin_row_pitch)
        fix_pin_array.AddPadsToModule(self.draw)

        # draw the body dimension
        body_width = pad_pitch * (pads_per_row - 1) + pcbnew.FromMM(self.body_width_offset_mm*2)
        body_height = pcbnew.FromMM(self.body_height_mm)
        self.draw.SetLayer(pcbnew.F_Fab)    # Fabrication layer
        self.draw.SetLineThickness( pcbnew.FromMM( 0.12 ) ) #Default per KLC F5.1 as of 12/2018
        self.draw.Box(0, 0, body_width, body_height)

        # draw the 1st pin indicator
        first_pin_x = - pad_pitch * (pads_per_row - 1) / 2
        first_pin_y = - row_pitch / 2
        indicator_w = pcbnew.FromMM(1.0)
        indicator_h = indicator_w*1.732/2
        indicator_x = first_pin_x
        indicator_y = first_pin_y - pad_length / 2 - pcbnew.FromMM(0.5)
        self.draw.SetLayer(pcbnew.F_SilkS)    # Silk layer
        self.draw.SetLineThickness( pcbnew.FromMM( 0.12 ) ) #Default per KLC F5.1 as of 12/2018
        self.draw.Line(indicator_x, indicator_y, indicator_x - indicator_w/2, indicator_y - indicator_h)
        self.draw.Line(indicator_x, indicator_y, indicator_x + indicator_w/2, indicator_y - indicator_h)
        self.draw.Line(indicator_x - indicator_w/2, indicator_y - indicator_h, indicator_x + indicator_w/2, indicator_y - indicator_h)

        #reference and value
        text_size = self.GetTextSize()  # IPC nominal
        text_px = body_width/2 + text_size
        self.draw.Value(0, 0, text_size)
        self.draw.Reference(-text_px, 0, text_size, orientation_degree=90)

        self.module.SetAttributes(pcbnew.PAD_ATTRIB_SMD)

HiroseFX23Wizard().register()
