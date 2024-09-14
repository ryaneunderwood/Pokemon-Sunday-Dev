import os
import re

def parse_tm_file(tm_file_path):
    pokemon_moves = {}
    current_move = None
    
    try:
        with open(tm_file_path, 'r', encoding='utf-8') as tm_file:
            for line in tm_file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    current_move = line[1:-1]
                elif current_move and line:
                    for pokemon in line.split(','):
                        pokemon = pokemon.strip()
                        if pokemon:
                            if pokemon not in pokemon_moves:
                                pokemon_moves[pokemon] = set()
                            pokemon_moves[pokemon].add(current_move)
    except FileNotFoundError:
        print(f"Error: The file {tm_file_path} was not found.")
        return None
    except IOError as e:
        print(f"Error reading the file {tm_file_path}: {e}")
        return None
    
    return pokemon_moves

def update_pokemon_file(pokemon_file_path, pokemon_moves):
    if pokemon_moves is None:
        return

    updated_lines = []
    changes_made = 0
    
    try:
        with open(pokemon_file_path, 'r', encoding='utf-8') as pokemon_file:
            content = pokemon_file.read()
        
        pokemon_entries = content.split('#-------------------------------')
        
        for i, entry in enumerate(pokemon_entries):
            if entry.strip():
                # Preserve the line break after #-------------------------------
                updated_entry = '#-------------------------------\n' + entry.lstrip() if i > 0 else entry

                match = re.search(r'InternalName=(\w+)', updated_entry)
                if match:
                    current_pokemon = match.group(1)
                    
                    tutor_moves = pokemon_moves.get(current_pokemon, set())
                    if tutor_moves:
                        moves_match = re.search(r'(Moves=.*?)(\s|$)', updated_entry, re.DOTALL)
                        if moves_match:
                            moves_end = moves_match.end()
                            tutor_moves_line = f'TutorMoves={",".join(sorted(tutor_moves))}\n'
                            updated_entry = updated_entry[:moves_end] + tutor_moves_line + updated_entry[moves_end:]
                            changes_made += 1

                updated_lines.append(updated_entry)
        
        if changes_made > 0:
            with open(pokemon_file_path, 'w', encoding='utf-8') as pokemon_file:
                pokemon_file.write(''.join(updated_lines))
            print(f"Successfully updated {pokemon_file_path} with TutorMoves for {changes_made} Pokémon.")
        else:
            print(f"No changes were made to {pokemon_file_path}. No matching Pokémon found.")
    except FileNotFoundError:
        print(f"Error: The file {pokemon_file_path} was not found.")
    except IOError as e:
        print(f"Error updating the file {pokemon_file_path}: {e}")

def main():
    tm_file_path = os.path.join('PBS', 'tm.txt')
    pokemon_file_path = os.path.join('PBS', 'pokemon.txt')
    
    pokemon_moves = parse_tm_file(tm_file_path)
    if pokemon_moves:
        update_pokemon_file(pokemon_file_path, pokemon_moves)
    else:
        print("Failed to parse TM file. Pokemon file not updated.")

if __name__ == "__main__":
    main()