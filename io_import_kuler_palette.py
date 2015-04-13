# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from urllib.request import urlretrieve
from urllib.parse   import urlparse

bl_info = {
    "name": "Kuler Palette Importer",
    "author": "Ted VjBros",
    "version": (0, 1, 0),
    "blender": (2, 75, 0),
    "location": "Tools > Kuler Importer",
    "description": "Tool to import Adobe Kuler palettes to Paint palettes",
    "category": "Import-Export"}

class KulerImporterOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "palette.kuler_importer"
    bl_label = "Import Kuler Palette"

    KulerUrl = bpy.props.StringProperty(name="Kuler Url")
    
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        print()
        
        KulerParsedUrl = urlparse(self.KulerUrl)
        
        if (KulerParsedUrl.netloc != "color.adobe.com"):
            self.report({'ERROR'}, "Not a Adobe Kuler Url : " + self.KulerUrl)
            return {'CANCELLED'}
        
        KulerPath = KulerParsedUrl.path
        KulerPath = KulerPath.split('-')
        KulerPathLength = len(KulerPath)
        print(KulerPath[KulerPathLength - 3 : KulerPathLength - 1])
        if (KulerPath[KulerPathLength - 3 : KulerPathLength - 1] != ['color', 'theme']):
            self.report({'ERROR'}, "Adobe Url Incorrect\nEx : https://color.adobe.com/Theme-9-color-theme-5838502/")
            return {'CANCELLED'}    

        
        
        KulerId = KulerPath[-1][:-1]
        KulerName = ''.join(KulerPath[:-3])[1:]
        
        print("Import Palette : " + KulerId + " " + KulerName)
        
        SizeX = 100
        SizeY = 10

        TemporaryDirectory = context.user_preferences.filepaths.temporary_directory
        
        if (len(TemporaryDirectory) == 0):
            self.report({'ERROR'}, "Blender Temporary Directory not set!\nCheck in User Preferences > File > Temp")
            return {'CANCELLED'}    
            
        
        try:
            KulerFile = urlretrieve("https://color.adobe.com/api/v2/themes/" + KulerId + ".png?width=" + str(SizeX) + "&height=" + str(SizeY), TemporaryDirectory + "kuler.png")
        except Exception as e:
            raise NameError("Cannot load image " + KulerId)
        
        bpy.ops.image.open(filepath = KulerFile[0])

        KulerImage = bpy.data.images['kuler.png']

        KulerPixel = KulerImage.pixels

        Y = (SizeY * SizeX * 4) /2
        Xspace = (SizeX * 4) / 5
        Xoffset = Xspace/2

        
        NewKulerPalette = bpy.data.palettes.new(str(KulerName))
        
        for i in range(0, 5):
            X = int(Xoffset) + (i * int(Xspace)) + int(Y)
            Xr = KulerPixel[ X   ]
            Xg = KulerPixel[ X+1 ]
            Xb = KulerPixel[ X+2 ]
            Xa = KulerPixel[ X+3 ]

            print("Import Colors : " + str(Xr) + " " + str(Xg) + " " + str(Xb) + " " + str(Xa))
            
            NewKulerColor = NewKulerPalette.colors.new()
            NewKulerColor.color[0] = Xr
            NewKulerColor.color[1] = Xg
            NewKulerColor.color[2] = Xb

        

        return {'FINISHED'}

             

def menu_func(self, context):
    self.layout.operator(KulerImporterOperator.bl_idname)
    
def register():
    bpy.utils.register_class(KulerImporterOperator)
    bpy.types.VIEW3D_PT_tools_brush.append(menu_func)
    


def unregister():
    bpy.types.VIEW3D_PT_tools_brush.remove(menu_func)    
    bpy.utils.unregister_class(KulerImporterOperator)

if __name__ == "__main__":
    register()
