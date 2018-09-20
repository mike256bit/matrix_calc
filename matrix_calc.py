"""
TO DO:
  Replace BOM_Dict with a function that procedurally generates BOM additions as it goes through the part counter.
  Must be a way to simplfy and refactor.
  Possible to also add mass value?
  Generate classes for each part. Yes. Rewrite the code to work with classes. Part class __ini__ might have values for mass,
    lenght, qty, other
  
    
"""
  


import datetime

def data_writer(start_data, ext_len_data, data_list, write_file):
  
  w_f = open(write_file, "a")
  
  w_f.write("\n\n"+str(datetime.datetime.now())[:-7]+"\n")
  for each in [start_data, ext_len_data]:
      w_f.write(each+"\n")
      print(each)
  for each_list in data_list:
    for each in each_list:
      w_f.write(each+"\n")
      print(each)
  
  w_f.close()

def mass_estimate(BOM_dictionary, h_len, v_len):
  #initial mass (grams)
  mass_list = [2 * h_len, 2 * v_len, 533, 117, 95, 227, 57, 334]
  qty_list = list(BOM_dictionary.values())

  mass_total_grams = 0
  i = 0
  for i in range(len(qty_list[:8])):
    mass_total_grams += mass_list[i] * qty_list[i]
  
  mass_total_pounds = mass_total_grams // 454

  return_report = []
  for each in ["(no cabinets)", "(with ~20lb cabinets)"]:
    return_report.append("Estimated Frame Weight {}: {}kg ({} lbs)".format(each, mass_total_grams//1000, mass_total_pounds))
    mass_total_grams += 10000 * qty_list[-1]
    mass_total_pounds =  mass_total_grams // 454
  
  return return_report

def BOM_printer(BOM_dictionary):
  return_report = []
  return_report.append("QTY.\tPART")
  return_report.append("-----\t-----")
  for k, v in BOM_dictionary.items():
    return_report.append("  "+str(v)+"\t"+str(k))
  return_report.append("")
  
  return return_report

def part_counter(h_list, v_list, wp_list, f_list, d_matrix):
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
  BOM_dict["Cabinet"] = d_matrix[0] * d_matrix[1]

  return BOM_dict

def dimension_reporter(dim_lists):
  
  return_report = []
  for each in dim_lists:
    return_report.append(each[0])
    for item in range(1, len(each)):
      return_report.append("\t" + str(item) + "  " + str(each[item]))
    return_report.append("")
  
  return return_report

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

def conflict_handler(dynamic_list, static_list):

  min_con = 90

  for each in dynamic_list:
    for i in range(1, len(static_list)):
      conflict = round(static_list[i] - each)
      if abs(conflict) < min_con:
        print("\nWARNING! Wall Plate Conflict: Vertical at {}mm is within {}mm of wall plate at suggested {}mm.".format(static_list[i], abs(conflict), each))
        if conflict > 0:
          dynamic_list.insert(dynamic_list.index(each), str(each + conflict + min_con) + "* (" + str(each) + ")")
          dynamic_list.remove(each)
          print("\n  Action: Conflict moved to the right from {}mm by {}mm.".format(each, conflict + min_con))
        elif conflict < 0:
          dynamic_list.insert(dynamic_list.index(each), str(each + (min_con - abs(conflict))) + "* (" + str(each) + ")")
          dynamic_list.remove(each)
          print("\n  Action: Conflict moved to the right from {}mm by {}mm.".format(each, min_con - abs(conflict)))
        
  return dynamic_list

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
  from sys import argv, exit
  
  data_file = open(argv[1], "r")
  
  #initialize data
  data_from_file = data_file.readline().split()
  
  data_file.close()

  disp = (int(data_from_file[0]), int(data_from_file[1]))
  disp_matrix = (int(data_from_file[2]), int(data_from_file[3]))
  corner = (int(data_from_file[4]), int(data_from_file[5]))
  flag_dims = (160, 80) #wide, tall
  flag_pad = (15, (flag_dims[1] - corner[1])//2)
  end_buffer = 10
  
  #collect extrusion lengths
  (hor_len, vert_len) = hor_vert_len(flag_pad, disp, disp_matrix, corner)
  
  #find vertical positions (the 30 is from half the extrusion width)
  final_vert_list = space_finder(flag_dims[0] - 30 - end_buffer, disp[0], disp_matrix[0], corner[0], hor_len)
  final_vert_list.insert(0, "Vertical Extrusion Positions (mm):\n  From left edge to extrusion centerline")

  #find flag positions
  final_flag_list = space_finder(flag_pad[1] + corner[1]/2, disp[1], disp_matrix[1], corner[1], vert_len)
  final_flag_list.insert(0, "Vertical Flag Positions (mm):\n  From bottom edge to flag centerline")

  #find horizontal extrusion positions
  final_hor_list = conflict_handler(hor_pos_normal(vert_len), final_flag_list)
  final_hor_list.insert(0, "Horizontal Extrusion Positions (mm):\n  From bottom edge of vertical extrusion to horizontal extrusion centerline")

  #find wall plate positions (and avoid conflict with vertical positions)
  final_wall_list = conflict_handler(wall_pos(hor_len, end_buffer), final_vert_list)
  final_wall_list.insert(0, "Wall Plate Positions (mm):\n  From left edge to plate centerline")
  
  #collate data into passable variables
  initial_data = "\nInitial data:\n  Display Size (mm): {}mm x {}mm\n  Matrix Size (W x H): {} x {}\n  Corner Spacing (W X H): {}mm x {}mm\n".format(disp[0], disp[1],disp_matrix[0], disp_matrix[1], corner[0], corner[1])
  
  length_data = "\n  Horizontal Extrusion Length: {}mm\n  Vertical Extrusion Length: {}mm\n".format(hor_len - end_buffer * 2, vert_len)
  
  dimension_data = dimension_reporter([final_hor_list, final_wall_list, final_vert_list, final_flag_list])
  
  bom_data = BOM_printer(part_counter(final_hor_list[1:], final_vert_list[1:], final_wall_list[1:], final_flag_list[1:], disp_matrix))

  mass_data = mass_estimate(part_counter(final_hor_list[1:], final_vert_list[1:], final_wall_list[1:], final_flag_list[1:], disp_matrix), hor_len, vert_len)

  data_writer(initial_data, length_data, [dimension_data, bom_data, mass_data], argv[1])

if __name__ == "__main__":
  main()
