# import pandas as pd
# import sys
# # if len(sys.argv)>2:
# #     key = sys.argv[2]
# #     df = pd.read_hdf(fpath, key=key)
# # else:
# df = pd.read_hdf(fpath)

# df.to_csv(sys.stdout, index=False)
fpath = "TRAAAGR128F425B14B.h5"

import hdf5_getters
h5 = hdf5_getters.open_h5_file_read(fpath)
duration = hdf5_getters.get_duration(h5)
print(duration)
print(hdf5_getters.get_title(h5))
print(hdf5_getters.get_artist_name(h5))
h5.close()
