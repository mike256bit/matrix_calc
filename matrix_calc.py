def mass_estimate(BOM_dictionary, h_len, v_len, d_matrix):
  #initial mass (grams)
  mass_list = [2 * h_len, 2 * v_len, 533, 117, 95, 227, 57, 334]
  qty_list = list(BOM_dictionary.values())

  mass_total_grams = 0
  i = 0
  for i in range(len(qty_list[:8])):
    mass_total_grams += mass_list[i] * qty_list[i]
  
  mass_total_pounds = mass_total_grams // 454

  mass_cabs = 5000 * (d_matrix[0] * d_matrix[1])
  mass_cabs_pounds = mass_cabs // 454
  
  print("\n\nEstimated Frame Weight (no cabinets): {}kg ({} lbs).".format(mass_total_grams//1000, mass_total_pounds))
  print("\nEstimated Total Weight (with cabinets): {}kg ({} lbs).".format((mass_total_grams + mass_cabs)//1000, mass_total_pounds + mass_cabs_pounds))

  # hor_mass = BOM_dictionary["Horizontal Extrusions"] * h_len * 2 #2 grams per mm
  # vert_mass = BOM_dictionary["Vertical Extrusions"] * v_len * 2
  # wp_mass = BOM_dictionary["Wall Plates"] * 533
  


def BOM_printer(BOM_dictionary):
  print("\n QTY.\tPART")
  print("-----\t-----")
  for k, v in BOM_dictionary.items():
    print("  "+str(v)+"\t"+str(k))

def part_counter(h_list, v_list, wp_list, f_list):
  h_ext_count = len(h_list) #derive from list
  v_ext_count = len(v_list) #derive from list
  wp_count = h_ext_count * len(wp_list) #derive from list * h_ext, covers the top and bottom brackets
  v_bkt_count = h_ext_count * v_ext_count #derive from h_count * v_count (*2 for vert side brackets)
  flag_count = v_ext_count * len(f_list) #derive from flag list * v_count
  
  BOM_dict = {}
  BOM_dict["Horizonal Extrusions"] = h_ext_count
  BOM_dict["Vertical Extrusions"] = v_ext_count
  BOM_dict["Wall Plates"] = wp_count
  BOM_dict["Hor. Ext. Top Bkts"] = wp_count
  BOM_dict["Hor. Ext. Bottom Bkts"] = wp_count
  BOM_dict["Vertical Plate Bkts"] = v_bkt_count
  BOM_dict["Vertical Attach Bkts"] = v_bkt_count * 2
  BOM_dict["Flags"] = flag_count
  BOM_dict["M6 Cap Screw"] = 4 * wp_count + 8 * v_bkt_count
  BOM_dict["M6 T-SLot Nut"] = BOM_dict["M6 Cap Screw"]
  BOM_dict["M6 C'sunk Screw"] = 4 * flag_count
  BOM_dict["M6 Wingnut"] = 4 * wp_count + 2 * v_bkt_count

  return BOM_dict

def dimension_reporter(dim_lists):

  for each in dim_lists:
    print(each[0])
    for item in range(1, len(each)):
      print("\t", item, each[item])
    print()

def hor_pos_normal(vert_len):
  
  hor_min = 800
  hor_buffer = 100
  hor_count = 1 + ((vert_len - 2 * hor_buffer) // hor_min)  #assumes vert_len > 800, all cases
  hor_span = hor_min * (hor_count - 1)
  hor_first = int(vert_len / 2 - hor_span / 2) #from vert bottom edge to hor ext. CL 
 
  hor_list = [hor_first]
  for each in range(1, hor_count):
    hor_list.append(hor_list[0] + each * hor_min)

  return hor_list

def vert_wall_conflict(wall_list, vert_pos_list):

  min_con = 90

  for each in wall_list:
    for i in range(1, len(vert_pos_list)):
      conflict = round(vert_pos_list[i] - each)
      if abs(conflict) < min_con:
        print("\nWARNING! Wall Plate Conflict: Vertical at {}mm is within {}mm of wall plate at suggested {}mm.".format(vert_pos_list[i], abs(conflict), each))
        if conflict > 0:
          wall_list.insert(wall_list.index(each), str(each + conflict + min_con) + "* (" + str(each) + ")")
          wall_list.remove(each)
          print("\n  Action: Conflict moved to the right from {}mm by {}mm.".format(each, conflict + min_con))
        elif conflict < 0:
          wall_list.insert(wall_list.index(each), str(each + (min_con - abs(conflict))) + "* (" + str(each) + ")")
          wall_list.remove(each)
          print("\n  Action: Conflict moved to the right from {}mm by {}mm.".format(each, min_con - abs(conflict)))
        
  return wall_list

def wall_pos(hor_len, end_buff):
  wall_count = 1
  max_wall = 1000
  wall_first = 200 + end_buff #dist to wall CL from left edge

  wall_list = [wall_first]
  wall_last = hor_len - end_buff * 2 - wall_first
  wall_span = wall_last - wall_first

  if wall_span > max_wall:
    wall_count += wall_span // max_wall
    span_dist = wall_span / wall_count

  for each in range(1, wall_count):
    wall_list.append(round(wall_list[0] + each * span_dist))
  
  wall_list.append(wall_last)

  return wall_list

def space_finder(init_pos, disp_dim, disp_matrix_num, corner_dim, ext_len):
  
  space_list = [init_pos]
  space_list.append(init_pos + disp_dim)

  for each in range(2, disp_matrix_num):
    space_value = each * (disp_dim + corner_dim) + init_pos - corner_dim
    space_list.append(space_value)
  
  space_list.append(ext_len - init_pos)
  
  return space_list

def hor_vert_len(flag_pad, disp, disp_matrix, corner):

  h_v = []
  for each in range(2):
    h_v.append(flag_pad[each] * 2 + corner[each] + disp_matrix[each] * disp[each] + (disp_matrix[each]-2) * corner[each])
  
  return (h_v[0], h_v[1])

def main():

  #initialize data
  disp = (500, 500) #wide, tall
  corner = (30, 30) # wide, tall
  disp_matrix = (4, 4) #wide, tall
  flag_dims = (160, 80) #wide, tall
  
  flag_pad = (15, (flag_dims[1] - corner[1])//2)
  end_buffer = 10
  
  #collect extrusion lengths
  (hor_len, vert_len) = hor_vert_len(flag_pad, disp, disp_matrix, corner)
  
  #find vertical positions (the 30 is from half the extrusion width)
  final_vert_list = space_finder(flag_dims[0] - 30 - end_buffer, disp[0], disp_matrix[0], corner[0], hor_len)
  final_vert_list.insert(0, "Vertical Extrusion Positions (mm):\n  From left edge to extrusion centerline")

  #find horizontal extrusion positions
  final_hor_list = hor_pos_normal(vert_len)
  final_hor_list.insert(0, "Horizontal Extrusion Positions (mm):\n  From bottom edge of vertical extrusion to horizontal extrusion centerline")

  #find wall plate positions (and avoid conflict with vertical positions)
  final_wall_list = vert_wall_conflict(wall_pos(hor_len, end_buffer), final_vert_list)
  final_wall_list.insert(0, "Wall Plate Positions (mm):\n  From left edge to plate centerline")

  #find flag positions
  final_flag_list = space_finder(flag_pad[1] + corner[1]/2, disp[1], disp_matrix[1], corner[1], vert_len)
  final_flag_list.insert(0, "Vertical Flag Positions (mm):\n  From bottom edge to flag centerline")
  

  print("\nInitial data:\n  Display Size (mm): {}mm x {}mm\n  Matrix Size (W x H): {} x {}".format(disp[0], disp[1],disp_matrix[0], disp_matrix[1]))

  print("\n  Horizontal: {}mm\n  Vertical: {}mm\n".format(hor_len - end_buffer * 2, vert_len))

  dimension_reporter([final_vert_list, final_hor_list, final_wall_list, final_flag_list])

  BOM_printer(part_counter(final_hor_list[1:], final_vert_list[1:], final_wall_list[1:], final_flag_list[1:]))

  mass_estimate(part_counter(final_hor_list[1:], final_vert_list[1:], final_wall_list[1:], final_flag_list[1:]), hor_len, vert_len, disp_matrix)

if __name__ == "__main__":
  main()