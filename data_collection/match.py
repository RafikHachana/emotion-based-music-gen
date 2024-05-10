import hdf5_getters
import pandas as pd
import glob
from pathlib import Path
from tqdm import tqdm
import re
SPOTIFY_CSV_PATH = "~/Downloads/archive(6)/dataset.csv"
MSD_ROOT_PATH ="/home/rafik/Downloads/lmd_matched_h5"

df = pd.read_csv(SPOTIFY_CSV_PATH)

print(df.columns)
# exit()
print(MSD_ROOT_PATH+"/**/*.h5")
# print(glob.glob(MSD_ROOT_PATH+"/**/*.h5", recursive=True))
# print(Path(MSD_ROOT_PATH).rglob("*.h5"))

cnt = 0
matches = 0
multiple_matches = 0
non_matches = []

result = []
for file_path in tqdm(Path(MSD_ROOT_PATH).rglob("*.h5")):
    h5 = hdf5_getters.open_h5_file_read(file_path)
    title = hdf5_getters.get_title(h5).decode()
    artist = hdf5_getters.get_artist_name(h5).decode()
    # album = hdf5_getters.get_release(h5).decode()

    # print(album)



    
    spotify_entry = df[(df['artists'].str.contains(re.escape(artist), na=False, case=False)) & (df['track_name'] == title)]
    # title_only = df[ (df['track_name']== title)]
    # if len(spotify_entry) > 1:
    #    spotify_entry = spotify_entry[df['album_name'] == album]
    if len(spotify_entry) > 1:
        multiple_matches += 1
    if len(spotify_entry):
        matches += len(spotify_entry)
        # print(title, "-", artist, file_path.name[:-3])
        for i in range(len(spotify_entry)):
            result.append(( spotify_entry.iloc[i]['track_id'], file_path.name[:-3]))
    h5.close()
    cnt += 1
    # if cnt == 50:
    #     break

matched = pd.DataFrame(result, columns=['track_id', 'msd_track_id'])

final_result = pd.merge(df, matched, on='track_id', how='inner')

print(final_result.head)
print("Total matches", matches)
print("Songs with multiple matches", multiple_matches)
# print(non_matches)

final_result.to_csv("matched.csv")
