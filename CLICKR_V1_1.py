#this is a free addon, you can use, edit and share this addon as you please! If you have any suggestions for the code, please let me know


bl_info = {
    "name" : "CLICKR",
    "author" : "OliverJPost",
    "description" : "Place objects, with some randomization",
    "blender" : (2, 81, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


import bpy
import random
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils import Matrix, Vector
import numpy as np

#                                    888 
#                                    888 
#                                    888 
#88888b.   8888b.  88888b.   .d88b.  888 
#888  888 .d888888 888  888 88888888 888 
#888 d88P 888  888 888  888 Y8b.     888 
#88888P"  "Y888888 888  888  "Y8888  888 
#888                                     
#888                                     
#888

class CLICKR_PT_PANEL(bpy.types.Panel):
    bl_idname = "CLICKR_PT_Panel"
    bl_label = "CLICKR"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CLICKR"   


    def draw(self, context):
        settings  = context.scene.CLICKR
        layout = self.layout
        col= layout.column()
        col.operator("clickr.modal", text="Start Clicking", icon='MOUSE_LMB') 

    

class C_SURFACE_PT_PANEL(bpy.types.Panel):
    bl_idname = "SURFACE_PT_Panel"
    bl_label = "Ground Surface"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CLICKR"   
    
    def draw(self, context):
        layout = self.layout
        col= layout.column()
        col.operator("clickr.surface", text="Select ground surface", icon='MESH_PLANE')
        col.label(text = "Surface is: {}".format(bpy.context.scene.CLICKR.clickr_surface))        
   

class C_RANDOMIZATION_PT_PANEL(bpy.types.Panel):
    bl_idname = "RANDOMIZATION_PT_Panel"
    bl_label = "Randomize"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CLICKR"   
    
    def draw(self, context):
        settings  = context.scene.CLICKR
        layout = self.layout
        col= layout.column()        
        col.prop(settings, 'clickr_rotation', slider=True)
        col.prop(settings, 'clickr_askew', slider = True)
        col.prop(settings, 'clickr_scale') 


class C_OPTIONS_PT_PANEL(bpy.types.Panel):
    

    bl_idname = "OPTIONS_PT_Panel"
    bl_label = "Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CLICKR"   
    
    def draw(self, context):        
        settings  = context.scene.CLICKR
        layout = self.layout
        col= layout.column()
        col.prop(settings, 'clickr_collection')
        col.prop(settings, 'clickr_align')
        col.prop(settings, 'clickr_linked')
        col.operator("clickr.origin", text="Move origins to bottom", icon='DOT')     


# .d888                            888    d8b                            
#d88P"                             888    Y8P                            
#888                               888                                   
#888888 888  888 88888b.   .d8888b 888888 888  .d88b.  88888b.  .d8888b  
#888    888  888 888 "88b d88P"    888    888 d88""88b 888 "88b 88K      
#888    888  888 888  888 888      888    888 888  888 888  888 "Y8888b. 
#888    Y88b 888 888  888 Y88b.    Y88b.  888 Y88..88P 888  888      X88 
#888     "Y88888 888  888  "Y8888P  "Y888 888  "Y88P"  888  888  88888P'



def add_to_collection(object_to_move):
    """
    checks if the CLICKR collection exists and moves the object to this collection
    """   
    
    #only run the code when the user has checked the checkbox
    if bpy.context.scene.CLICKR.clickr_collection == True:
        #name for the collection that will be created
        collection_name = 'CLICKR' 
        
        #try if it exists, otherwise create it
        try: 
            collection = bpy.data.collections[collection_name]
        except:
            collection = bpy.data.collections.new(name= collection_name )
            bpy.context.scene.collection.children.link(collection)
        
        #move object to new collection and unlink from old collection
        obj = object_to_move
        old_collections = []
        for collection in obj.users_collection:
            try:
                bpy.data.collections[collection.name].objects.unlink(obj)
            except:
                bpy.context.scene.collection.objects.unlink(obj)
        bpy.data.collections[collection_name].objects.link(obj)


def choose_object(self):
    """
    chooses a random object from the objects that were selected when the user pressed 'start clicking' and duplicates it
    """   
      
    #choose a random object from the pool of objects
    self.clickr_pick= random.choice(self.obj_pool)
    
    #deselect all and make the pick active
    bpy.ops.object.select_all(action='DESELECT')
    self.clickr_pick.select_set(state=True)
    bpy.context.view_layer.objects.active = self.clickr_pick
    
    #duplicate this object and make it clickr_dupl
    bpy.ops.object.duplicate(linked=bpy.context.scene.CLICKR.clickr_linked, mode='TRANSLATION')
    self.clickr_dupl=bpy.context.active_object
    
    #move to CLICKR collection 
    add_to_collection(self.clickr_dupl)                

def randomization(self):
    """
    applies randomization in scale and rotation on the currently selected object
    """
    
    #get a random positive or negative 
    if random.random() < 0.5: 
        pos_neg= 1 
    else:
        pos_neg= -1 

    
    #randomize scale
    scale_random= 1+random.randrange(10)/10*bpy.context.scene.CLICKR.clickr_scale*pos_neg
    bpy.ops.transform.resize(value=(scale_random, scale_random, scale_random))
    
    #randomize Z rotation
    rotation_random= bpy.context.scene.CLICKR.clickr_rotation/200 *random.randrange(10)*pos_neg
    bpy.ops.transform.rotate(value=rotation_random, orient_axis='Z')

    #randomize XY rotation
    askew_random= bpy.context.scene.CLICKR.clickr_askew/30 *random.randrange(10)*pos_neg
    bpy.ops.transform.rotate(value=askew_random, orient_axis='Y')
    bpy.ops.transform.rotate(value=askew_random, orient_axis='X')

    
def origin_to_bottom(ob, matrix=Matrix(), use_verts=False):
    """
    moves the origin of the object to the bottom of it's bounding box. This code was shared by the user batFINGER on Blender StackExchange in the post named "Set origin to bottom center of multiple objects"
    """
    me = ob.data
    mw = ob.matrix_world
    if use_verts:
        data = (v.co for v in me.vertices)
    else:
        data = (Vector(v) for v in ob.bound_box)


    coords = np.array([matrix @ v for v in data])
    z = coords.T[2]
    mins = np.take(coords, np.where(z == z.min())[0], axis=0)

    o = Vector(np.mean(mins, axis=0))
    o = matrix.inverted() @ o
    me.transform(Matrix.Translation(-o))

    mw.translation = mw @ o    


#         888                                              
#         888                                              
#         888                                              
# .d8888b 888  8888b.  .d8888b  .d8888b   .d88b.  .d8888b  
#d88P"    888     "88b 88K      88K      d8P  Y8b 88K      
#888      888 .d888888 "Y8888b. "Y8888b. 88888888 "Y8888b. 
#Y88b.    888 888  888      X88      X88 Y8b.          X88 
# "Y8888P 888 "Y888888  88888P'  88888P'  "Y8888   88888P'
 
                         
class CLICKR_OP(bpy.types.Operator):
    """
    Modal for placing the objects
    """
    bl_idname = "clickr.modal"
    bl_label = "CLICKR modal"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            """
            Moves the object to the raycasted snap position on a pre-selected object. This part of the code was shared by the user 'lemon' on Blender StackExchange in the post named "How to move object while tracking to mouse cursor with a modal operator?"
            """
            #Get the mouse position thanks to the event            
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y

            #Contextual active object, 2D and 3D regions
            self.object = self.clickr_dupl
            region = bpy.context.region
            region3D = bpy.context.space_data.region_3d

            #The direction indicated by the mouse position from the current view
            self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
            #The view point of the user
            self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
            #The 3D location in this direction
            self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)

            plane = bpy.data.objects[bpy.context.scene.CLICKR.clickr_surface]
            self.loc_on_plane = None
            z = Vector( (0,0,1) )
            self.normal = z
            if plane:
                world_mat_inv = plane.matrix_world.inverted()
                # Calculates the ray direction in the target space
                rc_origin = world_mat_inv @ self.view_point
                rc_destination = world_mat_inv @ self.world_loc
                rc_direction = (rc_destination - rc_origin).normalized()
                hit, loc, norm, index = plane.ray_cast( origin = rc_origin, direction = rc_direction )
                self.loc_on_plane = loc
                if hit:
                    self.world_loc = plane.matrix_world @ loc
                    if bpy.context.scene.CLICKR.clickr_align == True:
                        norm.rotate( plane.matrix_world.to_euler('XYZ') )
                        self.normal = norm.normalized()
            if self.object:
                self.object.location = self.world_loc
                if bpy.context.scene.CLICKR.clickr_align == True:
                    self.object.rotation_euler = z.rotation_difference( self.normal ).to_euler()
                
                
        elif event.type == 'LEFTMOUSE' and event.value == "RELEASE": 
            """
            chooses a new object, this means the old object stays at the location it was when the user released LMB
            """
            choose_object(self)
            randomization(self)    

        
        
        elif event.type == 'RET' and event.value == "RELEASE":
            """
            Get a new random object, making sure its not the same as the last one. Chooses a new object, and deletes the one that was being moved. 
            """
            
            #remember the old name
            old_name=self.clickr_dupl
            
            #make sure only the CLICKR object is selected and active
            bpy.ops.object.select_all(action='DESELECT')
            self.clickr_dupl.select_set(state=True)
            context.view_layer.objects.active = self.clickr_dupl

            #choose a new random object and make sure it's not the same as the last one. To prevent issues stop trying after 5 tries
            i=0
            self.clickr_pick = random.choice(self.obj_pool)
            while self.clickr_pick.name == old_name.name[:-4] and i<5: #this [:-4] part is not optimal, it is a workaround for the suffix that is added when an object is copied. This is needed to check it against the original objects when picking a new random
                self.clickr_pick = random.choice(self.obj_pool)
                i+=1
            
            #delete the old object    
            bpy.ops.object.delete()     
            
            #select the new object and make it clickr_dupl
            self.clickr_pick.select_set(state=True)
            context.view_layer.objects.active = self.clickr_pick
            bpy.ops.object.duplicate(linked=bpy.context.scene.CLICKR.clickr_linked, mode='TRANSLATION')
            self.clickr_dupl = bpy.context.active_object

            #add the randomizations
            randomization(self)
            
            #move to CLICKR collection 
            add_to_collection(self.clickr_dupl)     
            
            
        elif event.type in {'ESC'}:
            """
            Cancels the modal, deleting the object that was currently being placed 
            """
            
            #delete the currently moving object
            bpy.ops.object.select_all(action='DESELECT')
            self.clickr_dupl.select_set(state=True)
            context.view_layer.objects.active = self.clickr_dupl
            bpy.ops.object.delete() 
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if bpy.context.selected_objects:
                
                #check if a surface was selected
                try:
                    bpy.data.objects[bpy.context.scene.CLICKR.clickr_surface]
                except:
                    self.report({'WARNING'}, "No ground surface selected")
                    return {'CANCELLED'}
                
                #create a list of objects that are selected when starting the modal
                self.obj_pool = []
                objs=bpy.context.selected_objects
                for obj in objs:
                    if obj.name == bpy.context.scene.CLICKR.clickr_surface:
                        if len(objs) == 1:
                            self.report({'WARNING'}, "You have only your ground surface selected. You probably don't want to start clicking with that.")
                            return {'CANCELLED'}
                        else:
                            pass    
                    else:
                        self.obj_pool.append(obj)
                
                choose_object(self)
                randomization(self)


                
                #these variables are needed for the snapping. This part of the invoke code was shared by the user 'lemon' as referenced above
                self.mouse_pos = [0,0]
                self.loc = [0,0,0]
                self.object = None
                self.view_point = None
                self.view_vector = None
                self.world_loc = None
                self.loc_on_plane = None
                self.normal = None
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                self.report({'WARNING'}, "No objects selected")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class CLICKR_SURFACE(bpy.types.Operator):
    """
    selects the surface objects will snap to
    """
    bl_idname = "clickr.surface"
    bl_label = "CLICKR Surface"
    bl_description = "Make the current active object your CLICKR ground surface"
    
    def execute(self, context):    
        try:
            bpy.context.scene.CLICKR.clickr_surface = bpy.context.active_object.name
        
        #return warning when no objects was selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'}
    
class CLICKR_ORIGIN(bpy.types.Operator):
    """
    moves origin of objects to the bottom of their bounding box
    """
    bl_idname = "clickr.origin"
    bl_label = "CLICKR Origin"
    bl_description = "Move origins to bottom of objects"
    
    def execute(self, context):    
        try:
            for obj in bpy.context.selected_objects:
                origin_to_bottom(obj)
        #return warning when no objects were selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'}     
    
                 

#         888    d8b 888 
#         888    Y8P 888 
#         888        888 
#888  888 888888 888 888 
#888  888 888    888 888 
#888  888 888    888 888 
#Y88b 888 Y88b.  888 888 
# "Y88888  "Y888 888 888
            
class CLICKR_SETTINGS(bpy.types.PropertyGroup):
    clickr_surface: bpy.props.StringProperty(
        name='clickr_surface',
        description="surface CLICKR places objects on",
        default= 'None',
        )
    clickr_linked: bpy.props.BoolProperty(
        name="Create instances",
        description="",
        default=True
        )
    clickr_collection: bpy.props.BoolProperty(
        name="Move to CLICKR collection",
        description="",
        default=False
        )
    clickr_align: bpy.props.BoolProperty(
        name="Align rotation to surface",
        description="",
        default=False
        )
    clickr_rotation: bpy.props.IntProperty(
        name='Z Rotation',
        subtype="PERCENTAGE",
        min=0,
        max=100)
    clickr_scale: bpy.props.FloatProperty(
        name='Scale',
        step = 1,
        precision = 2,        
        min=0.0,
        soft_max=1,
        max=10)
    clickr_askew: bpy.props.FloatProperty(
        name='Skewness',
        step = 1,
        precision = 2,        
        min=0.0,
        soft_max=0.1,
        max=10)

    
classes = (
    CLICKR_PT_PANEL,
    C_SURFACE_PT_PANEL,
    C_RANDOMIZATION_PT_PANEL,
    C_OPTIONS_PT_PANEL,    
    CLICKR_OP,
    CLICKR_SETTINGS,
    CLICKR_SURFACE,
    CLICKR_ORIGIN
    )

# Register
def register():
    for cls in classes:    
        bpy.utils.register_class(cls)
    bpy.types.Scene.CLICKR = bpy.props.PointerProperty(type=CLICKR_SETTINGS)


# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.CLICKR

if __name__ == "__main__":
    register()
