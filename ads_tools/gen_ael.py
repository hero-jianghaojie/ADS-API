# Generate AEL scripts for ADS
import os
from pathlib import Path

# 定位项目根目录（codex_wrk 输出目录位于根目录下；本脚本位于 ADS/ads_tools/ 下，上溯三级）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ael1 = '''/* Create ADS cells */
decl lib_name = "codex_lib";
decl lib = deFindLib(lib_name);
if (lib == NULL) {
    lib = deCreateLib(lib_name);
    println("Created library: " + lib_name);
}
decl function createCellView(cellName) {
    decl cell = deFindCell(lib, cellName);
    if (cell == NULL) {
        cell = deCreateCell(lib, cellName);
        deCreateView(cell, "schematic");
        println("Created cell: " + cellName);
    } else {
        println("Cell exists: " + cellName);
    }
    return cell;
}
createCellView("impedance_coupler");
createCellView("input_matching");
createCellView("output_matching");
createCellView("single_ended_pa");
createCellView("balanced_pa");
createCellView("substrate");
println("");
println("All cells created! Open each schematic and place components.");
'''

with open(str(_PROJECT_ROOT / 'codex_wrk' / 'create_circuits.ael'), 'w', encoding='utf-8') as f:
    f.write(ael1)
print("create_circuits.ael saved")

ael2 = '''/* Generate schematics (run create_circuits.ael first) */
decl lib = deFindLib("codex_lib");
if (lib == NULL) {
    println("ERROR: codex_lib not found. Run create_circuits.ael first.");
    stop;
}

decl function placeComp(cellName, compType, instName, x, y) {
    decl cell = deFindCell(lib, cellName);
    if (cell == NULL) {
        println("Cell not found: " + cellName);
        return;
    }
    decl view = deFindView(cell, "schematic");
    if (view == NULL) {
        println("View not found for: " + cellName);
        return;
    }
    decl win = deOpenDesign(view);
    decl comp = deNewComponent(win, compType, instName, x, y);
    return comp;
}

decl function setParam(win, comp, param, value) {
    deSetComponentParams(win, comp, param, value);
}

/* Substrate */
decl subCell = deFindCell(lib, "substrate");
if (subCell) {
    decl subView = deFindView(subCell, "schematic");
    if (subView) {
        decl subWin = deOpenDesign(subView);
        deSetSubstrateParams(subWin, "MSub1",
            "H", "0.508 mm",
            "Er", "3.55",
            "Mur", "1",
            "Cond", "5.8e7",
            "Hu", "1.0e+33 mm",
            "T", "0.035 mm",
            "TanD", "0.0027",
            "Rough", "0 mm");
        deSetSubstrate(subWin, "MSub1");
        deSetModelMode(subWin, "MSub1", "microstrip");
        deSaveDesign(subWin);
        deCloseDesign(subWin);
        println("Substrate configured: Rogers 4003C");
    }
}

/* Coupler */
decl cpWin = deOpenDesign(deFindView(deFindCell(lib, "impedance_coupler"), "schematic"));
if (cpWin) {
    decl p1 = deNewComponent(cpWin, "PORT", "P1", 100, 200);
    setParam(cpWin, p1, "Z", "50 Ohm");
    setParam(cpWin, p1, "Num", "1");
    decl p2 = deNewComponent(cpWin, "PORT", "P2", 500, 200);
    setParam(cpWin, p2, "Z", "50 Ohm");
    setParam(cpWin, p2, "Num", "2");
    decl p3 = deNewComponent(cpWin, "PORT", "P3", 300, 400);
    setParam(cpWin, p3, "Z", "50 Ohm");
    setParam(cpWin, p3, "Num", "3");
    decl p4 = deNewComponent(cpWin, "PORT", "P4", 300, 0);
    setParam(cpWin, p4, "Z", "50 Ohm");
    setParam(cpWin, p4, "Num", "4");
    decl ml1 = deNewComponent(cpWin, "MLIN", "TL1", 200, 200);
    setParam(cpWin, ml1, "W", "1.12 mm");
    setParam(cpWin, ml1, "L", "18.75 mm");
    setParam(cpWin, ml1, "Subst", "MSub1");
    decl ml2 = deNewComponent(cpWin, "MLIN", "TL2", 400, 200);
    setParam(cpWin, ml2, "W", "1.12 mm");
    setParam(cpWin, ml2, "L", "18.75 mm");
    setParam(cpWin, ml2, "Subst", "MSub1");
    decl ml3 = deNewComponent(cpWin, "MLIN", "TL3", 300, 300);
    setParam(cpWin, ml3, "W", "1.12 mm");
    setParam(cpWin, ml3, "L", "18.75 mm");
    setParam(cpWin, ml3, "Subst", "MSub1");
    decl ml4 = deNewComponent(cpWin, "MLIN", "TL4", 300, 100);
    setParam(cpWin, ml4, "W", "1.12 mm");
    setParam(cpWin, ml4, "L", "18.75 mm");
    setParam(cpWin, ml4, "Subst", "MSub1");
    decl tee = deNewComponent(cpWin, "MTEE", "Tee1", 300, 200);
    setParam(cpWin, tee, "W1", "1.12 mm");
    setParam(cpWin, tee, "W2", "1.12 mm");
    setParam(cpWin, tee, "W3", "1.12 mm");
    setParam(cpWin, tee, "Subst", "MSub1");
    decl rs1 = deNewComponent(cpWin, "MRSTUB", "RS1", 360, 260);
    setParam(cpWin, rs1, "W", "1.12 mm");
    setParam(cpWin, rs1, "R", "8.0 mm");
    setParam(cpWin, rs1, "Angle", "60 deg");
    setParam(cpWin, rs1, "Subst", "MSub1");
    decl rs2 = deNewComponent(cpWin, "MRSTUB", "RS2", 240, 140);
    setParam(cpWin, rs2, "W", "1.12 mm");
    setParam(cpWin, rs2, "R", "8.0 mm");
    setParam(cpWin, rs2, "Angle", "60 deg");
    setParam(cpWin, rs2, "Subst", "MSub1");
    deSaveDesign(cpWin);
    deCloseDesign(cpWin);
    println("impedance_coupler: components placed");
}

/* Input Matching */
decl inWin = deOpenDesign(deFindView(deFindCell(lib, "input_matching"), "schematic"));
if (inWin) {
    decl pin = deNewComponent(inWin, "PORT", "RF_IN", 50, 200);
    setParam(inWin, pin, "Z", "50 Ohm");
    setParam(inWin, pin, "Num", "1");
    decl pout = deNewComponent(inWin, "PORT", "TO_GATE", 500, 200);
    setParam(inWin, pout, "Z", "50 Ohm");
    setParam(inWin, pout, "Num", "2");
    decl cap = deNewComponent(inWin, "C", "C_DC", 150, 200);
    setParam(inWin, cap, "C", "100 pF");
    decl ml1 = deNewComponent(inWin, "MLIN", "TL1", 250, 200);
    setParam(inWin, ml1, "W", "2.8 mm");
    setParam(inWin, ml1, "L", "10.0 mm");
    setParam(inWin, ml1, "Subst", "MSub1");
    decl ml2 = deNewComponent(inWin, "MLIN", "TL2", 380, 200);
    setParam(inWin, ml2, "W", "1.5 mm");
    setParam(inWin, ml2, "L", "12.0 mm");
    setParam(inWin, ml2, "Subst", "MSub1");
    decl bias = deNewComponent(inWin, "MLIN", "TL_Bias", 250, 100);
    setParam(inWin, bias, "W", "0.5 mm");
    setParam(inWin, bias, "L", "15.0 mm");
    setParam(inWin, bias, "Subst", "MSub1");
    decl ind = deNewComponent(inWin, "L", "L_Gate", 250, 50);
    setParam(inWin, ind, "L", "100 nH");
    decl vgg = deNewComponent(inWin, "PORT", "VGG", 250, 0);
    setParam(inWin, vgg, "Z", "50 Ohm");
    setParam(inWin, vgg, "Num", "3");
    deSaveDesign(inWin);
    deCloseDesign(inWin);
    println("input_matching: components placed");
}

println("");
println("Done! Open each schematic and wire the components.");
'''

with open(str(_PROJECT_ROOT / 'codex_wrk' / 'generate_schematics.ael'), 'w', encoding='utf-8') as f:
    f.write(ael2)
print("generate_schematics.ael saved")
