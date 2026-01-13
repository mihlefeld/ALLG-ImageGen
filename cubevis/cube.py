import re
import sys

class Cube:
    def __init__(self, mdefs) -> None:
        self.mdefs = mdefs
        self.pieces = {}
        self.moves = {}
        self.max_cycles = {}
        self.read_move_definitions(mdefs)
    
    def getName(self):
        return "Cube"

    def read_move_definition(self, move):
        cycles = re.findall(r'\([A-Za-z0-9+\- ]+\)', move)
        move_name = move.split()[0][:-1]
        list_cycles = []
        max_cycle_len = 0
        for cycle in cycles:
            pieces = cycle[1:-1].split()
            cylce_list = []
            for piece in pieces:
                piece_name = piece
                orientation_change = 0
                if str.isnumeric(piece[-1]) and len(piece) > 2 and "+" in piece or "-" in piece:
                    orientation_change = int(piece[-2:])
                    piece_name = piece[:-2]
                cylce_list.append((piece_name, orientation_change))
                self.pieces[piece_name] = (piece_name, 0)
            max_cycle_len = max(len(cylce_list), max_cycle_len)
            list_cycles.append(cylce_list)
        self.max_cycles[move_name] = max_cycle_len
        self.moves[move_name] = list_cycles

    def is_solved(self):
        for k, (p, o) in self.pieces.items():
            if not (k == p and o == 0):
                return False
        return True

    def read_move_definitions(self, move_definitions):
        mdefs = move_definitions.split("\n")
        for mdef in mdefs:
            self.read_move_definition(mdef)
        
        for move in self.moves.keys():
            cycles = 1
            self.move(move)
            while not self.is_solved():
                self.move(move)
                cycles += 1
                if cycles > 6:
                    print(f"Takes more than 6 cycles to go back to solved, likely an error in a move definition {move} {self.getName()}", file=sys.stderr)
                    self.reset()
                    break
            self.max_cycles[move] = cycles

    def to_reference_rotation(self, scramble=True):
        return ""

    def move(self, m):
        if m == "":
            return
        ms = re.findall(r"[\d]?[A-z]+[\d']*", m)
        if len(ms) > 1:
            for m_ in ms:
                self.move(m_)
            return
        if m not in self.moves:
            move_count = 1
            for num in re.findall(r"[\d]?[A-z]+([\d]+)", m.replace("'", "")):
                move_count = int(num)
            for mod in re.findall(r"'", m):
                move_count *= -1
            move_name = re.search(r"[\d]?[A-z]+", m).group(0)
            if move_name not in self.max_cycles:
                print(f"Illegal move \"{move_name}\", ignoring")
                return
            move_count = move_count % self.max_cycles[move_name]

            for i in range(move_count):
                self.move(move_name)
            return
        
        if m not in self.max_cycles:
            print(f"Illegal move \"{move_name}\", ignoring")
            return

        cycles = self.moves[m]
        for cycle in cycles:
            sources = []
            for piece, oc in cycle:
                sources.append(piece)
            destinations =  sources[1:] + [sources[0]]
            tmp = []
            for (source, oc) in cycle:
                piece, ori = self.pieces[source]
                ori = (ori + oc) % len([c for c in piece if c.isalpha()])
                tmp += [(piece, ori)]
            for dest, piece in zip(destinations, tmp):
                self.pieces[dest] = piece

    def reset(self):
        for k in self.pieces.keys():
            self.pieces[k] = (k, 0)
    
    def scramble(self, moves):
        self.reset()
        self.move(moves)

    def debug(self):
        for loc, piece in self.pieces.items():
            print(loc, piece)

    def pieces_to_cycles(self, name):
        visited = set()
        cycles = []
        for k, v in self.pieces.items():
            if k in visited:
                continue
            startKey = k
            visited.add(startKey)
            curKey = k
            curV = v
            cycle = [curV]
            while startKey != curV[0]:
                curKey = curV[0]
                visited.add(curKey)
                curV = self.pieces[curKey]
                cycle.append(curV)
            cycles.append(cycle)
        
        move_def = f"{name}:"
        for cycle in cycles:
            if len(cycle) == 1 and cycle[0][1] == 0:
                continue
            inverse_cycle = cycle[::-1]
            move_def += " (" + " ".join([f"{p}" + f"+{o % len(inverse_cycle[0][0])}" * (o != 0) for (p, o) in inverse_cycle]) + ")"
        return move_def


class Skewb(Cube):
    def __init__(self) -> None:
        super().__init__("""l: (UFL-1 DFR-1 DBL-1) (DLF+1) (L F D)
L: (URF-1 DLF-1 ULB-1) (UFL+1) (U F L)
r: (DFR-1 UBR-1 DBL-1) (DRB+1) (R B D)
R: (URF-1 ULB-1 DRB-1) (UBR+1) (R U B)
b: (ULB-1 DLF-1 DRB-1) (DBL+1) (L D B)
B: (UBR-1 UFL-1 DBL-1) (ULB+1) (U L B)
F: (UFL-1 UBR-1 DFR-1) (URF+1) (F U R) 
f: (URF-1 DRB-1 DLF-1) (DFR+1) (F R D)
S: (URF-1) (UFL+1) (ULB+1) (UBR-1) (R U) (F B)
H: (URF+1) (UFL-1) (ULB-1) (UBR+1) (R U) (F B)
s: (UBR-1) (ULB+1) (DRB-1) (DBL+1) (U D) (R B)
h: (UBR+1) (ULB-1) (DRB+1) (DBL-1) (U D) (R B)      
x: (F U B D) (URF+1 UBR-1 DRB+1 DFR-1) (UFL-1 ULB+1 DBL-1 DLF+1)
y: (F L B R) (URF UFL ULB UBR) (DFR DLF DBL DRB)
z: (U R D L) (URF-1 DFR+1 DLF-1 UFL+1) (UBR+1 DRB-1 DBL+1 ULB-1)""")
        
    def getName(self):
        return "Skewb"
    
    def to_reference_rotation(self, scramble=True):
        solved_piece = "URF" if scramble else "DFR"
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "x ", "x2 ", "x' ", "z ", "z' "]
        second_rotations = ["", "y", "y2", "y'"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces[solved_piece] == (solved_piece, 0):
                    return (fr + sr).strip()



class Megaminx(Cube):
    def __init__(self) -> None:
        super().__init__("""U: (UR+0 UF+0 UL+0 UA+0 UB+0) (URF+0 UFL+0 ULA+0 UAB+0 UBR+0) (U+0)
R: (UR+1 RB+0 RH+0 RC+0 RF+1) (URF+1 UBR+1 RBH+0 RHC+0 RCF+1)
L: (UL+1 LF+0 LD+0 LE+0 LA+1) (ULA+1 UFL+1 LFD+0 LDE+0 LEA+1)
F: (UF+0 RF+1 FC+0 FD+1 LF+0) (UFL+1 URF+0 RCF+1 FCD+1 LFD+0)
Bl: (UA LA+1 AE AG+1 BA) (UAB+1 ULA LEA+1 AEG+1 BAG)
Br: (UB+1 BA+0 BG+0 BH+1 RB+0) (UBR+1 UAB+1 BAG+0 BGH+1 RBH+0)
Dfr: (FC+0 RC+1 CH+0 CI+0 CD+1) (FCD+0 RCF+1 RHC+1 CHI+0 CID+1)
Dfl: (LD FD CD+1 DI DE+1) (LFD FCD CID+1 DIE+1 LDE+1)
Dbr: (RH BH GH+1 HI+1 CH) (RHC+1 RBH BGH GIH-1 CHI)
Dbl: (LE DE+1 EI EG+1 AE) (LEA+1 LDE DIE+1 EIG+1 AEG)
Db: (AG EG+1 GI GH+1 BG) (BAG AEG EIG+1 GIH+1 BGH+1)
D: (CI HI GI EI DI) (CID+1 CHI-1 GIH EIG DIE)
x: (AEG-1 EIG-1 DIE LDE-1 LEA) (AE+1 EG EI+1 DE LE) (URF+1 UBR+1 RBH RHC RCF+1) (UR+1 RB+0 RH+0 RC+0 RF+1) (LFD-1 ULA BAG-1 GIH+1 CID+1) (LF+1 UA BG HI CD+1) (UFL-1 UAB BGH+1 CHI FCD) (UL BA+1 GH+1 CI FD) (UB BH+1 CH FC UF+1) (LD+1 LA AG GI+1 DI) (F U B H C) (D L A G I)
y: (RCF+1 LFD-1 LEA+1 BAG RBH-1) (RHC FCD LDE AEG BGH) (UR+0 UF+0 UL+0 UA+0 UB+0) (URF+0 UFL+0 ULA+0 UAB+0 UBR+0) (DI EI GI HI CI) (DIE EIG GIH+1 CHI-1 CID) (EG GH+1 CH+1 CD DE) (LA+1 BA RB+1 RF+1 LF+1) (FD LE AG BH RC) (FC LD AE BG RH) (F L A B R) (G H C D E)
z: (UR RC CD+1 LD UL+1) (UF RF+1 FC FD+1 LF) (UA RB CH DI LE) (UB RH CI DE LA) (URF RCF+1 FCD+1 LFD UFL+1) (ULA+2 UBR RHC CID+1 LDE) (UAB RBH CHI DIE LEA) (U R C D L) (AE BA+1 BH HI+1 EI) (AG BG+1 GH GI+1 EG) (AEG BAG+2 BGH+2 GIH+2 EIG) (B H I E A)
xl: (UR FC DI EG+1 BA+1) (UF FD DE+1 AE UA+1) (UL+1 LF LD LE LA+1) (UB+1 RF CD+1 EI AG) (URF FCD DIE+1 AEG UAB+2) (UFL+1 LFD LDE LEA+1 ULA+1) (UBR+2 RCF CID+1 EIG+1 BAG+2) (U F D E A) (RB+1 RC CI+1 GI BG) (RH CH+1 HI+1 GH BH) (RBH+2 RHC CHI+1 GIH BGH) (B R C I G)""")
        
    def getName(self):
        return "Megaminx"
    
    def to_reference_rotation(self, scramble=True):
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "x ", "x2 ", "x2' ", "x' ", "y ", "y' ", "y2' ", "xl2 ", "xl2 y ", "xl2 y2 "]
        second_rotations = ["", "z", "z2", "z2'", "z'"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces["RCF"] == ("RCF", 0):
                    return (fr + sr).strip()
        
class TwoByTwo(Cube):
    def __init__(self) -> None:
        super().__init__("""U: (URF UFL ULB UBR)
R: (URF+1 UBR-1 DRB+1 DFR-1)
F: (URF-1 DFR+1 DLF-1 UFL+1)
D: (DFR DRB DBL DLF)
L: (UFL-1 DLF+1 DBL-1 ULB+1)
B: (UBR+1 ULB-1 DBL+1 DRB-1)
x: (URF+1 UBR-1 DRB+1 DFR-1) (UFL-1 ULB+1 DBL-1 DLF+1)
y: (URF UFL ULB UBR) (DFR DLF DBL DRB)
z: (URF-1 DFR+1 DLF-1 UFL+1) (UBR+1 DRB-1 DBL+1 ULB-1)""")

        
    def getName(self):
        return "2x2"
    
    def to_reference_rotation(self, scramble=True):
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "x ", "x2 ", "x' ", "z ", "z' "]
        second_rotations = ["", "y", "y2", "y'"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces["DBL"] == ("DBL", 0):
                    return (fr + sr).strip()
    
class ThreeByThree(Cube):
    def __init__(self) -> None:
        super().__init__("""U: (UF UL UB UR) (URF UFL ULB UBR)
R: (UR BR DR FR) (URF+1 UBR-1 DRB+1 DFR-1)
F: (UF-1 FR-1 DF-1 FL-1) (URF-1 DFR+1 DLF-1 UFL+1)
D: (DF DR DB DL) (DFR DRB DBL DLF)
L: (UL FL DL BL) (UFL-1 DLF+1 DBL-1 ULB+1)
B: (UB-1 BL-1 DB-1 BR-1) (UBR+1 ULB-1 DBL+1 DRB-1)
u: (UF UL UB UR) (URF UFL ULB UBR) (FR-1 FL-1 BL-1 BR-1) (F L B R)
r: (UR BR DR FR) (URF+1 UBR-1 DRB+1 DFR-1) (UF-1 UB-1 DB-1 DF-1) (U B D F)
f: (UF-1 FR-1 DF-1 FL-1) (URF-1 DFR+1 DLF-1 UFL+1) (UR-1 DR-1 DL-1 UL-1) (U R D L)
d: (DF DR DB DL) (DFR DRB DBL DLF) (FR-1 BR-1 BL-1 FL-1) (F R B L)
l: (UL FL DL BL) (UFL-1 DLF+1 DBL-1 ULB+1) (UF-1 DF-1 DB-1 UB-1) (U F D B)
b: (UB-1 BL-1 DB-1 BR-1) (UBR+1 ULB-1 DBL+1 DRB-1) (UR-1 UL-1 DL-1 DR-1) (U L D R)
Uw: (UF UL UB UR) (URF UFL ULB UBR) (FR-1 FL-1 BL-1 BR-1) (F L B R)
Rw: (UR BR DR FR) (URF+1 UBR-1 DRB+1 DFR-1) (UF-1 UB-1 DB-1 DF-1) (U B D F)
Fw: (UF-1 FR-1 DF-1 FL-1) (URF-1 DFR+1 DLF-1 UFL+1) (UR-1 DR-1 DL-1 UL-1) (U R D L)
Dw: (DF DR DB DL) (DFR DRB DBL DLF) (FR-1 BR-1 BL-1 FL-1) (F R B L)
Lw: (UL FL DL BL) (UFL-1 DLF+1 DBL-1 ULB+1) (UF-1 DF-1 DB-1 UB-1) (U F D B)
Bw: (UB-1 BL-1 DB-1 BR-1) (UBR+1 ULB-1 DBL+1 DRB-1) (UR-1 UL-1 DL-1 DR-1) (U L D R)
M: (UF-1 DF-1 DB-1 UB-1) (U F D B)
S: (UR-1 DR-1 DL-1 UL-1) (U R D L)
E: (FR-1 BR-1 BL-1 FL-1) (F R B L)
x: (UR BR DR FR) (URF+1 UBR-1 DRB+1 DFR-1) (UL BL DL FL) (UFL-1 ULB+1 DBL-1 DLF+1) (UF-1 UB-1 DB-1 DF-1) (U B D F)
y: (UF UL UB UR) (URF UFL ULB UBR) (DF DL DB DR) (DFR DLF DBL DRB) (FR-1 FL-1 BL-1 BR-1) (F L B R)
z: (UF-1 FR-1 DF-1 FL-1) (URF-1 DFR+1 DLF-1 UFL+1) (UB-1 BR-1 DB-1 BL-1) (UBR+1 DRB-1 DBL+1 ULB-1) (UR-1 DR-1 DL-1 UL-1) (U R D L)""")
    
    def getName(self):
        return "3x3"
    
    def to_reference_rotation(self, scramble=True):
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "x ", "x2 ", "x' ", "z ", "z' "]
        second_rotations = ["", "y", "y2", "y'"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces["DBL"] == ("DBL", 0):
                    return (fr + sr).strip()
    
class Pyraminx(Cube):
    def __init__(self) -> None:
        super().__init__("""U: (BR FB RF) (BFR+1) (bfr+1)
R: (FB BD DF) (FBD+1) (fbd+1)
L: (RF+1 DF RD+1) (FDR+1) (fdr+1)
B: (BR RD+1 BD+1) (BRD+1) (brd+1)
S: (FB DF+1 RF+1)
H: (FB+1 RF+1 DF)
u: (bfr+1)
r: (fbd+1)
l: (fdr+1)
b: (brd+1)
F: (FDR+1 BFR-1 FBD) (fdr+1 bfr-1 fbd) (DF RF+1 FB+1)
Lw: (BRD+1 BFR FDR-1) (brd+1 bfr fdr-1) (RF RD+1 BR+1)
Rw: (FBD-1 BFR BRD+1) (fbd-1 bfr brd+1) (FB+1 BR+1 BD)
D:  (FBD BRD-1 FDR+1) (fbd brd-1 fdr+1) (DF+1 BD RD+1)
x: (FDR BFR-1 BRD+1) (fdr bfr-1 brd+1) (RF+1 BR+1 RD) (FB BD DF) (FBD+1) (fbd+1)
xl: (BFR+1 FBD-1 BRD) (bfr+1 fbd-1 brd) (FB+1 BD BR+1) (RF+1 DF RD+1) (FDR+1) (fdr+1) 
y: (FDR+1 BRD FBD-1) (fdr+1 brd fbd-1) (DF+1 RD BD+1) (BR FB RF) (BFR+1) (bfr+1)
z: (FDR+1 BFR-1 FBD) (fdr+1 bfr-1 fbd) (DF RF+1 FB+1) (BD+1 RD BR+1) (BRD-1) (brd-1)""")
        
    def getName(self):
        return "Pyraminx"
    
    def to_reference_rotation(self, scramble=True):
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "x ", "x' ", "xl "]
        second_rotations = ["", "z", "z2"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces["FBD"] == ("FBD", 0):
                    return (fr + sr).strip()
            

class Octaminx(Cube):
    def __init__(self) -> None:
        super().__init__("""\
U: (WRGP WPOB WBZR) (WR WP WB) (W1 W2 W3) (R1 P1 B1) (R2 P2 B2)
R: (WRGP+2 WBZR-1 YGRZ-1) (WR ZR GR) (R1 R2 R3) (W2 Z3 G1) (W3 Z1 G2)
L: (WPOB+2 WRGP-1 YOPG-1) (WP GP OP) (P1 P2 P3) (W1 G1 O2) (W3 G3 O1)
B: (WBZR+2 WPOB-1 YZBO-1) (WB OB ZB) (B1 B2 B3) (W1 O3 Z1) (W2 O1 Z2)
F: (WRGP-1 YGRZ+2 YOPG-1) (GP GR GY) (G1 G2 G3) (R1 Y2 P3) (R3 Y1 P2)
Br: (WBZR-1 YZBO+2 YGRZ-1) (ZR ZB ZY) (Z1 Z2 Z3) (Y2 R2 B3) (Y3 R3 B1)
Bl: (WPOB-1 YOPG+2 YZBO-1) (OB OP OY) (O1 O2 O3) (P1 Y1 B3) (P3 Y3 B2)
D: (YOPG YGRZ YZBO) (GY ZY OY) (Y1 Y2 Y3) (G2 Z2 O2) (G3 Z3 O3)
Uw: (WRGP WPOB WBZR) (WR WP WB) (W1 W2 W3) (R1 P1 B1) (R2 P2 B2) (ZR GP OB) (GR OP ZB) (G1 O1 Z1) (P3 B3 R3) (R P B) (G O Z)
Rw: (WRGP+2 WBZR-1 YGRZ-1) (WR ZR GR) (R1 R2 R3) (W2 Z3 G1) (W3 Z1 G2) (GP WB ZY) (GY WP ZB) (P2 B1 Y2) (W1 Z2 G3) (W Z G) (P B Y)
Lw: (WPOB+2 WRGP-1 YOPG-1) (WP GP OP) (P1 P2 P3) (W1 G1 O2) (W3 G3 O1) (WR GY OB) (WB GR OY) (W2 G2 O3) (B2 R1 Y1) (O W G) (B R Y)
Bw: (WBZR+2 WPOB-1 YZBO-1) (WB OB ZB) (B1 B2 B3) (W1 O3 Z1) (W2 O1 Z2) (ZR WP OY) (ZY WR OP) (Z3 W3 O2) (Y3 R2 P1) (Z W O) (Y R P)
Fw: (WRGP-1 YGRZ+2 YOPG-1) (GP GR GY) (G1 G2 G3) (R1 Y2 P3) (R3 Y1 P2) (WP ZR OY) (WR ZY OP) (W3 Z3 O2) (R2 Y3 P1) (W Z O) (R Y P)
Brw: (WBZR-1 YZBO+2 YGRZ-1) (ZR ZB ZY) (Z1 Z2 Z3) (Y2 R2 B3) (Y3 R3 B1) (GY WR OB) (GR WB OY) (G2 W2 O3) (R1 B2 Y1) (G W O) (R B Y)
Blw: (WPOB-1 YOPG+2 YZBO-1) (OB OP OY) (O1 O2 O3) (P1 Y1 B3) (P3 Y3 B2) (WB GP ZY) (WP GY ZB) (B1 P2 Y2) (Z2 W1 G3) (Z W G) (B P Y)
Dw: (YOPG YGRZ YZBO) (GY ZY OY) (Y1 Y2 Y3) (G2 Z2 O2) (G3 Z3 O3) (GP ZR OB) (OP GR ZB) (O1 G1 Z1) (B3 P3 R3) (B P R) (O G Z)
eU: (WRGP WPOB WBZR) (WR WP WB) (W1 W2 W3) (R1 P1 B1) (R2 P2 B2)
eD: (YOPG YGRZ YZBO) (GY ZY OY) (Y1 Y2 Y3) (G2 Z2 O2) (G3 Z3 O3)
eR: (WRGP-1 YGRZ+2 YOPG-1) (GP GR GY) (G1 G2 G3) (R1 Y2 P3) (R3 Y1 P2)
eL: (WPOB-1 YOPG+2 YZBO-1) (OB OP OY) (O1 O2 O3) (P1 Y1 B3) (P3 Y3 B2)
eF: (WPOB+2 WRGP-1 YOPG-1) (WP GP OP) (P1 P2 P3) (W1 G1 O2) (W3 G3 O1)
eB: (WBZR-1 YZBO+2 YGRZ-1) (ZR ZB ZY) (Z1 Z2 Z3) (Y2 R2 B3) (Y3 R3 B1)
eBr: (WRGP+2 WBZR-1 YGRZ-1) (WR ZR GR) (R1 R2 R3) (W2 Z3 G1) (W3 Z1 G2)
eBl: (WBZR+2 WPOB-1 YZBO-1) (WB OB ZB) (B1 B2 B3) (W1 O3 Z1) (W2 O1 Z2)
eUw: (WRGP WPOB WBZR) (WR WP WB) (W1 W2 W3) (R1 P1 B1) (R2 P2 B2) (ZR GP OB) (GR OP ZB) (G1 O1 Z1) (P3 B3 R3) (P B R) (G O Z)
eRw: (WRGP-1 YGRZ+2 YOPG-1) (GP GR GY) (G1 G2 G3) (R1 Y2 P3) (R3 Y1 P2) (WP ZR OY) (WR ZY OP) (W3 Z3 O2) (R2 Y3 P1) (R Y P) (W Z O)
eLw: (WPOB-1 YOPG+2 YZBO-1) (OB OP OY) (O1 O2 O3) (P1 Y1 B3) (P3 Y3 B2) (WB GP ZY) (WP GY ZB) (B1 P2 Y2) (Z2 W1 G3) (Z W G) (B P Y)
eFw: (WPOB+2 WRGP-1 YOPG-1) (WP GP OP) (P1 P2 P3) (W1 G1 O2) (W3 G3 O1) (WR GY OB) (WB GR OY) (W2 G2 O3) (B2 R1 Y1) (B R Y) (W G O)
eBrw: (WRGP+2 WBZR-1 YGRZ-1) (WR ZR GR) (R1 R2 R3) (W2 Z3 G1) (W3 Z1 G2) (GP WB ZY) (GY WP ZB) (P2 B1 Y2) (W1 Z2 G3) (W Z G) (P B Y)
eBlw: (WBZR+2 WPOB-1 YZBO-1) (WB OB ZB) (B1 B2 B3) (W1 O3 Z1) (W2 O1 Z2) (ZR WP OY) (ZY WR OP) (Z3 W3 O2) (Y3 R2 P1) (Y R P) (Z W O)
eBw: (WBZR-1 YZBO+2 YGRZ-1) (ZR ZB ZY) (Z1 Z2 Z3) (Y2 R2 B3) (Y3 R3 B1) (GY WR OB) (GR WB OY) (G2 W2 O3) (R1 B2 Y1) (R B Y) (G W O)
eDw: (YOPG YGRZ YZBO) (GY ZY OY) (Y1 Y2 Y3) (G2 Z2 O2) (G3 Z3 O3) (GP ZR OB) (OP GR ZB) (O1 G1 Z1) (B3 P3 R3) (B P R) (O G Z)
H: (WRGP+2 WBZR+2 WPOB) (W1 W3 Z1) (W2 O1 G1)
S: (WRGP+2 WPOB WBZR+2) (W1 W2 G1) (W3 O1 Z1)
xr: (WRGP+2 WBZR-1 YGRZ-1) (WR ZR GR) (R1 R2 R3) (W2 Z3 G1) (W3 Z1 G2) (YOPG+1 WPOB+1 YZBO+2) (OP OB OY) (O3 O2 O1) (Y1 P1 B3) (Y3 P3 B2) (GP WB ZY) (GY WP ZB) (P2 B1 Y2) (W1 Z2 G3) (W Z G) (P B Y)
xl: (WPOB+2 WRGP-1 YOPG-1) (WP GP OP) (P1 P2 P3) (W1 G1 O2) (W3 G3 O1) (WBZR+1 YGRZ+2 YZBO+1) (ZB ZR ZY) (Z3 Z2 Z1) (R2 Y2 B3) (R3 Y3 B1) (WR GY OB) (WB GR OY) (W2 G2 O3) (B2 R1 Y1) (W G O) (B R Y)
y: (WRGP WPOB WBZR) (WR WP WB) (W1 W2 W3) (R1 P1 B1) (R2 P2 B2) (YGRZ YOPG YZBO) (ZY GY OY) (Y3 Y2 Y1) (Z2 G2 O2) (Z3 G3 O3) (ZR GP OB) (GR OP ZB) (G1 O1 Z1) (P3 B3 R3) (R P B) (G O Z)
z: (WRGP-1 YGRZ+2 YOPG-1) (GP GR GY) (G1 G2 G3) (R1 Y2 P3) (R3 Y1 P2) (WPOB+2 WBZR+1 YZBO+1) (OB WB ZB) (B3 B2 B1) (O3 W1 Z1) (O1 W2 Z2) (WP ZR OY) (WR ZY OP) (W3 Z3 O2) (R2 Y3 P1) (W Z O) (R Y P)
t: (WRGP+1) (YZBO-1) (WP+1 WR+1 GR+1 GP+1) (W3 R1 G1 P2) (WPOB-1 WBZR+2 YGRZ+1 YOPG+2) (WB+1 ZR+1 GY+1 OP+1) (W1 R2 G2 P3) (W2 R3 G3 P1) (B2 Z1 Y2 O2) (B1 Z3 Y1 O1) (B3 Z2 Y3 O3) (OB+1 ZB+1 ZY+1 OY+1) (P W R G) (O B Z Y)\
""")
        
    def to_reference_rotation(self, scramble=True):
        pieces_backup = {k: v for k, v in self.pieces.items()}
        first_rotations = ["", "t xl ", "t' ", "t ", "xr ", "xr' t ", "xl ", "xr' "]
        second_rotations = ["", "y", "y'"]
        for fr in first_rotations:
            for sr in second_rotations:
                self.pieces = {k: v for k, v in pieces_backup.items()}
                self.move(fr + sr)
                if self.pieces["YZBO"] == ("YZBO", 0):
                    return (fr + sr).strip()
        return ""
        
""" equivalences
{Y1 Y2 Y3}
{W1 W2 W3}
{G1 G2 G3}
{P1 P2 P3}
{R1 R2 R3}
{B1 B2 B3}
{O1 O2 O3}
{Z1 Z2 Z3}
{W R G P O B Z Y}
"""      

class FiveByFive(Cube):
    def __init__(self) -> None:
        super().__init__("""U: (UF UL UB UR) (URF UFL ULB UBR) (U1 U3 U5 U7) (U2 U4 U6 U8) (UF1 UL1 UB1 UR1) (UF2 UL2 UB2 UR2)
u: (UF UL UB UR) (URF UFL ULB UBR) (U1 U3 U5 U7) (U2 U4 U6 U8) (UF1 UL1 UB1 UR1) (UF2 UL2 UB2 UR2) (FR1-1 FL2-1 BL1-1 BR2-1) (R1 F1 L1 B1) (R2 F2 L2 B2) (R3 F3 L3 B3)
3u: (UF UL UB UR) (URF UFL ULB UBR) (U1 U3 U5 U7) (U2 U4 U6 U8) (UF1 UL1 UB1 UR1) (UF2 UL2 UB2 UR2) (FR1-1 FL2-1 BL1-1 BR2-1) (R1 F1 L1 B1) (R2 F2 L2 B2) (R3 F3 L3 B3) (FR-1 FL-1 BL-1 BR-1) (R4 F4 L4 B4) (R F L B) (R8 F8 L8 B8)
4u: (UF UL UB UR) (URF UFL ULB UBR) (U1 U3 U5 U7) (U2 U4 U6 U8) (UF1 UL1 UB1 UR1) (UF2 UL2 UB2 UR2) (FR1-1 FL2-1 BL1-1 BR2-1) (R1 F1 L1 B1) (R2 F2 L2 B2) (R3 F3 L3 B3) (FR-1 FL-1 BL-1 BR-1) (R4 F4 L4 B4) (R F L B) (R8 F8 L8 B8) (R5 F5 L5 B5) (R6 F6 L6 B6) (R7 F7 L7 B7) (FR2-1 FL1-1 BL2-1 BR1-1)
L: (UL FL DL BL) (UFL+2 DLF+1 DBL+2 ULB+1) (UL1 FL1 DL1 BL1) (UL2 FL2 DL2 BL2) (L1 L3 L5 L7) (L2 L4 L6 L8)
l: (UL FL DL BL) (UFL+2 DLF+1 DBL+2 ULB+1) (U1 F1 D1 B5) (U7 F7 D7 B3) (U8 F8 D8 B4) (UL1 FL1 DL1 BL1) (UB1+1 UF2+1 DF1+1 DB2+1) (UL2 FL2 DL2 BL2) (L1 L3 L5 L7) (L2 L4 L6 L8)
3l: (UF+1 DF+1 DB+1 UB+1) (UL FL DL BL) (UFL+2 DLF+1 DBL+2 ULB+1) (U1 F1 D1 B5) (U7 F7 D7 B3) (U2 F2 D2 B6) (U6 F6 D6 B2) (U8 F8 D8 B4) (UL1 FL1 DL1 BL1) (UB1+1 UF2+1 DF1+1 DB2+1) (UL2 FL2 DL2 BL2) (L1 L3 L5 L7) (L2 L4 L6 L8) (F D B U)
4l: (UF+1 DF+1 DB+1 UB+1) (UL FL DL BL) (UFL+2 DLF+1 DBL+2 ULB+1) (U1 F1 D1 B5) (U3 F3 D3 B7) (U5 F5 D5 B1) (U7 F7 D7 B3) (U2 F2 D2 B6) (U4 F4 D4 B8) (U6 F6 D6 B2) (U8 F8 D8 B4) (UF1+1 DF2+1 DB1+1 UB2+1) (UL1 FL1 DL1 BL1) (UB1+1 UF2+1 DF1+1 DB2+1) (UL2 FL2 DL2 BL2) (L1 L3 L5 L7) (L2 L4 L6 L8) (F D B U)
R: (UR BR DR FR) (URF+1 UBR+2 DRB+1 DFR+2) (UR1 BR1 DR1 FR1) (UR2 BR2 DR2 FR2) (R1 R3 R5 R7) (R2 R4 R6 R8)
r: (UR BR DR FR) (URF+1 UBR+2 DRB+1 DFR+2) (U3 B7 D3 F3) (U5 B1 D5 F5) (U4 B8 D4 F4) (UF1+1 UB2+1 DB1+1 DF2+1) (UR1 BR1 DR1 FR1) (UR2 BR2 DR2 FR2) (R1 R3 R5 R7) (R2 R4 R6 R8)
3r: (UF+1 UB+1 DB+1 DF+1) (UR BR DR FR) (URF+1 UBR+2 DRB+1 DFR+2) (U3 B7 D3 F3) (U5 B1 D5 F5) (U2 B6 D2 F2) (U4 B8 D4 F4) (U6 B2 D6 F6) (UF1+1 UB2+1 DB1+1 DF2+1) (UR1 BR1 DR1 FR1) (UR2 BR2 DR2 FR2) (R1 R3 R5 R7) (R2 R4 R6 R8) (F U B D)
4r: (UF+1 UB+1 DB+1 DF+1) (UR BR DR FR) (URF+1 UBR+2 DRB+1 DFR+2) (U1 B5 D1 F1) (U3 B7 D3 F3) (U5 B1 D5 F5) (U7 B3 D7 F7) (U2 B6 D2 F2) (U4 B8 D4 F4) (U6 B2 D6 F6) (U8 B4 D8 F8) (UF1+1 UB2+1 DB1+1 DF2+1) (UB1+1 DB2+1 DF1+1 UF2+1) (UR1 BR1 DR1 FR1) (UR2 BR2 DR2 FR2) (R1 R3 R5 R7) (R2 R4 R6 R8) (F U B D)
B: (UB+1 BL+1 DB+1 BR+1) (ULB+2 DBL+1 DRB+2 UBR+1) (UB1+1 BL2+1 DB1+1 BR2+1) (UB2+1 BL1+1 DB2+1 BR1+1) (B1 B3 B5 B7) (B2 B4 B6 B8)
b: (UB+1 BL+1 DB+1 BR+1) (ULB+2 DBL+1 DRB+2 UBR+1) (U1 L7 D5 R3) (U3 L1 D7 R5) (U2 L8 D6 R4) (UB1+1 BL2+1 DB1+1 BR2+1) (UR1+1 UL2+1 DL1+1 DR2+1) (UB2+1 BL1+1 DB2+1 BR1+1) (B1 B3 B5 B7) (B2 B4 B6 B8)
3b: (UL+1 DL+1 DR+1 UR+1) (UB+1 BL+1 DB+1 BR+1) (ULB+2 DBL+1 DRB+2 UBR+1) (U1 L7 D5 R3) (U3 L1 D7 R5) (U2 L8 D6 R4) (U4 L2 D8 R6) (U8 L6 D4 R2) (UB1+1 BL2+1 DB1+1 BR2+1) (UR1+1 UL2+1 DL1+1 DR2+1) (UB2+1 BL1+1 DB2+1 BR1+1) (B1 B3 B5 B7) (B2 B4 B6 B8) (R U L D)
4b: (UL+1 DL+1 DR+1 UR+1) (UB+1 BL+1 DB+1 BR+1) (ULB+2 DBL+1 DRB+2 UBR+1) (U1 L7 D5 R3) (U3 L1 D7 R5) (U5 L3 D1 R7) (U7 L5 D3 R1) (U2 L8 D6 R4) (U4 L2 D8 R6) (U6 L4 D2 R8) (U8 L6 D4 R2) (UL1+1 DL2+1 DR1+1 UR2+1) (UB1+1 BL2+1 DB1+1 BR2+1) (UR1+1 UL2+1 DL1+1 DR2+1) (UB2+1 BL1+1 DB2+1 BR1+1) (B1 B3 B5 B7) (B2 B4 B6 B8) (R U L D)
D: (DF DR DB DL) (DF1 DR1 DB1 DL1) (DFR DRB DBL DLF) (D1 D3 D5 D7) (D2 D4 D6 D8) (DF2 DR2 DB2 DL2)
d: (R5 B5 L5 F5) (R6 B6 L6 F6) (R7 B7 L7 F7) (FR2+1 BR1+1 BL2+1 FL1+1) (DF DR DB DL) (DF1 DR1 DB1 DL1) (DFR DRB DBL DLF) (D1 D3 D5 D7) (D2 D4 D6 D8) (DF2 DR2 DB2 DL2)
3d: (FR+1 BR+1 BL+1 FL+1) (R4 B4 L4 F4) (R B L F) (R8 B8 L8 F8) (R5 B5 L5 F5) (R6 B6 L6 F6) (R7 B7 L7 F7) (FR2+1 BR1+1 BL2+1 FL1+1) (DF DR DB DL) (DF1 DR1 DB1 DL1) (DFR DRB DBL DLF) (D1 D3 D5 D7) (D2 D4 D6 D8) (DF2 DR2 DB2 DL2)
4d: (FR1+1 BR2+1 BL1+1 FL2+1) (R1 B1 L1 F1) (R2 B2 L2 F2) (R3 B3 L3 F3) (FR+1 BR+1 BL+1 FL+1) (R4 B4 L4 F4) (R B L F) (R8 B8 L8 F8) (R5 B5 L5 F5) (R6 B6 L6 F6) (R7 B7 L7 F7) (FR2+1 BR1+1 BL2+1 FL1+1) (DF DR DB DL) (DF1 DR1 DB1 DL1) (DFR DRB DBL DLF) (D1 D3 D5 D7) (D2 D4 D6 D8) (DF2 DR2 DB2 DL2)
F: (UF+1 FR+1 DF+1 FL+1) (URF+2 DFR+1 DLF+2 UFL+1) (UF1+1 FR2+1 DF1+1 FL2+1) (UF2+1 FR1+1 DF2+1 FL1+1) (F1 F3 F5 F7) (F2 F4 F6 F8)
f: (UF+1 FR+1 DF+1 FL+1) (URF+2 DFR+1 DLF+2 UFL+1) (U5 R7 D1 L3) (U7 R1 D3 L5) (U6 R8 D2 L4) (UF1+1 FR2+1 DF1+1 FL2+1) (UL1+1 UR2+1 DR1+1 DL2+1) (UF2+1 FR1+1 DF2+1 FL1+1) (F1 F3 F5 F7) (F2 F4 F6 F8)
3f: (UF+1 FR+1 DF+1 FL+1) (UL+1 UR+1 DR+1 DL+1) (URF+2 DFR+1 DLF+2 UFL+1) (U5 R7 D1 L3) (U7 R1 D3 L5) (U4 R6 D8 L2) (U6 R8 D2 L4) (U8 R2 D4 L6) (UF1+1 FR2+1 DF1+1 FL2+1) (UL1+1 UR2+1 DR1+1 DL2+1) (UF2+1 FR1+1 DF2+1 FL1+1) (F1 F3 F5 F7) (F2 F4 F6 F8) (R D L U)
4f: (UF+1 FR+1 DF+1 FL+1) (UL+1 UR+1 DR+1 DL+1) (URF+2 DFR+1 DLF+2 UFL+1) (U1 R3 D5 L7) (U3 R5 D7 L1) (U5 R7 D1 L3) (U7 R1 D3 L5) (U2 R4 D6 L8) (U4 R6 D8 L2) (U6 R8 D2 L4) (U8 R2 D4 L6) (UF1+1 FR2+1 DF1+1 FL2+1) (UL1+1 UR2+1 DR1+1 DL2+1) (UR1+1 DR2+1 DL1+1 UL2+1) (UF2+1 FR1+1 DF2+1 FL1+1) (F1 F3 F5 F7) (F2 F4 F6 F8) (R D L U)
x: (UF1-1 UB2-1 DB1-1 DF2-1) (UF2-1 UB1-1 DB2-1 DF1-1) (UL1 BL1 DL1 FL1) (UL2 BL2 DL2 FL2) (UR1 BR1 DR1 FR1) (UR2 BR2 DR2 FR2) (F U B D) (F1 U1 B5 D1) (F2 U2 B6 D2) (F3 U3 B7 D3) (F4 U4 B8 D4) (F5 U5 B1 D5) (F6 U6 B2 D6) (F7 U7 B3 D7) (F8 U8 B4 D8) (R1 R3 R5 R7) (R2 R4 R6 R8) (L1 L7 L5 L3) (L2 L8 L6 L4) (UR BR DR FR) (URF+1 UBR-1 DRB+1 DFR-1) (UL BL DL FL) (UFL-1 ULB+1 DBL-1 DLF+1) (UF-1 UB-1 DB-1 DF-1)
y: (UF UL UB UR) (URF UFL ULB UBR) (U1 U3 U5 U7) (U2 U4 U6 U8) (UF1 UL1 UB1 UR1) (UF2 UL2 UB2 UR2) (FR1+1 FL2+1 BL1+1 BR2+1) (R1 F1 L1 B1) (R2 F2 L2 B2) (R3 F3 L3 B3) (FR+1 FL+1 BL+1 BR+1) (R4 F4 L4 B4) (R F L B) (R8 F8 L8 B8) (R5 F5 L5 B5) (R6 F6 L6 B6) (R7 F7 L7 B7) (FR2+1 FL1+1 BL2+1 BR1+1) (DF DL DB DR) (DF1 DL1 DB1 DR1) (DFR DLF DBL DRB) (D1 D7 D5 D3) (D2 D8 D6 D4) (DF2 DL2 DB2 DR2)
z: (UF+1 FR+1 DF+1 FL+1) (UL+1 UR+1 DR+1 DL+1) (UB+1 BR+1 DB+1 BL+1) (URF+2 DFR+1 DLF+2 UFL+1) (ULB+2 UBR+1 DRB+2 DBL+1) (U1 R3 D5 L7) (U3 R5 D7 L1) (U5 R7 D1 L3) (U7 R1 D3 L5) (U2 R4 D6 L8) (U4 R6 D8 L2) (U6 R8 D2 L4) (U8 R2 D4 L6) (UF1+1 FR2+1 DF1+1 FL2+1) (UL1+1 UR2+1 DR1+1 DL2+1) (UB1+1 BR2+1 DB1+1 BL2+1) (UR1+1 DR2+1 DL1+1 UL2+1) (UF2+1 FR1+1 DF2+1 FL1+1) (UB2+1 BR1+1 DB2+1 BL1+1) (F1 F3 F5 F7) (B1 B7 B5 B3) (F2 F4 F6 F8) (B2 B8 B6 B4) (R D L U)""")
        
    def getName(self):
        return "5x5"
"""Equivalences and unique orientations
2: UF1 UF2 UR1 UR2 UB1 UB2 UL1 UL2 DF1 DF2 DB1 DB2 DR1 DR2 DL1 DL2 FR1 FR2 FL1 FL2 BR1 BR2 BL1 BL2
{F1 F3 F5 F7}
{F2 F4 F6 F8}
{U1 U3 U5 U7}
{U2 U4 U6 U8}
{R1 R3 R5 R7}
{R2 R4 R6 R8}
{L1 L3 L5 L7}
{L2 L4 L6 L8}
{D1 D3 D5 D7}
{D2 D4 D6 D8}
{B1 B3 B5 B7}
{B2 B4 B6 B8}
{URF UFL ULB UBR DFR DLF DBL DRB}
"""    

class OctaminxRotations(Cube):
    def __init__(self) -> None:
        super().__init__("""\
xr: (W Z G) (P B Y)
xl: (W G O) (B R Y)
y: (R P B) (G O Z)
z: (W Z O) (R Y P)
t: (P W R G) (O B Z Y)""")