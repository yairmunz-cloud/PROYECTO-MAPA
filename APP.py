import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time
import base64


st.set_page_config(page_title="SUCURSALES", layout="wide", page_icon="🏢")

# LOGO ATLAS - Incrustado directo base64 para Cloud
B64_ATLAS_LOGO = """/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIbGNtcwIQAABtbnRyUkdCIFhZWiAH4gADABQACQAOAB1hY3NwTVNGVAAAAABzYXdzY3RybAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWhhbmSdkQA9QICwPUB0LIGepSKOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAABxjcHJ0AAABDAAAAAx3dHB0AAABGAAAABRyWFlaAAABLAAAABRnWFlaAAABQAAAABRiWFlaAAABVAAAABRyVFJDAAABaAAAAGBnVFJDAAABaAAAAGBiVFJDAAABaAAAAGBkZXNjAAAAAAAAAAV1UkdCAAAAAAAAAAAAAAAAdGV4dAAAAABDQzAAWFlaIAAAAAAAAPNUAAEAAAABFslYWVogAAAAAAAAb6AAADjyAAADj1hZWiAAAAAAAABilgAAt4kAABjaWFlaIAAAAAAAACSgAAAPhQAAtsRjdXJ2AAAAAAAAACoAAAB8APgBnAJ1A4MEyQZOCBIKGAxiDvQRzxT2GGocLiBDJKwpai5+M+s5sz/WRldNNlR2XBdkHWyGdVZ+jYgskjacq6eMstu+mcrH12Xkd/H5////2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAChAKMDASIAAhEBAxEB/8QAHQABAAEEAwEAAAAAAAAAAAAAAAgEBQcJAQMGAv/EAEQQAAECBAQEAwQGBggHAAAAAAECAwAEBREGByExCBJBURNhcSIyQpEJFCNSgbEVYnKCkqEWJDRDU7LB8BclM2PCw/H/xAAcAQABBQEBAQAAAAAAAAAAAAAABAUGBwgDAQL/xAA6EQABAwEGAwQIBAcBAQAAAAABAAIDBAUGESExURJBYSJxkdETI0JSgaGxwRQVYvAHMjNywuHxktL/2gAMAwEAAhEDEQA/ANmdVmzMTBQD9mg2Hmepihjkm5JPWOIEJCEIEJC8fK1hG8eGzTzlwxk/RV1LEM94BWkmXlG7KfmVDdLaL6+ZNgOpEeEhoxK7wQS1MgihaXOOQAzK9w4seGSFbdQYxBmRxT5fZZTTknP1oVCoo96Spg8dxB7KIPKk+SlAxCXOPi5xlms65Jybpw3QL2EjJOKDjo/7rosT+yLD1jCiGRv1JuYa5a4DKMK6bF/hw6UCW1Hkfpbhj8XZ/LxUvsYfSIVWYdW1hbCzEo0LgTFVfLi1fuIsE/xKjG1S4182Z83brMrIDqmWkmzb8VXvGD/C8o+/C9Ib3VMrtXK0qa6Fi0rQGUzT/d2vrisrHi2zbUvmOM5gdkplGbf5IuNP40M2pBV14ianB2mJBo/5UiMM+FHHhekfHppB7RS913bJcMDSx/8AhvkpSYV+kLxXIuNpxDh2n1Zg25lyK1yzo+ZWk/IRIHL3jJy7x5MMyrlTdw9PuEAMVcBpJJ6B25QfxIPlGtctWG0dTjNwQR7J3toYUMrZW65qLWjcCx6wExMMTt2n7HEfTvW6JiZafaStDqFpVqkhQIPpHbzC4FxrGqfKLiQxjk5OBMhOKqlGNgukT6ytm3dB3bV6adwdI2CZJcQGGc6qX4tMe+qVdlN5ukzCgH2jte3xJ2sod9bGHaGpZNloVR1vXSr7DJkd24veHL+4cvp1WVIR8ocCyQNxvePqFShCQhCBCQhCBCQhCBCRwo2STHMePzXzKo+VWBKniOsPpTLSqQENBXtvuE2S2gdST8gCToCY8JAGJXWKKSeRsUQxc44ADmSvI8QfEJR8jcMfWpkIn61MhSZGmJVZTigPeVuQgaEn8BqRGs/HGPq9mXiOYruIZ5c9PO3ACieRpF9EISdEpHb53N44zCzDrOa2MJ3Elcf8WdmFWShOiGUDRKEDokD56k3izNtk+cR6oqDKcOS1PdW7ENiQB7xjM7+Z23QdPrz5AfTbUVCEaawQnyjshGrHa3AJCEIF0ASEIQL3BDrHwtNxpH3CBfBCpHEGKrD+JKpgysylXos49TqhKL52n2FEFN9we4I0I6iPlaewimebuI9BwOISSeJkjS14xB1B5rZVwxcTsjnVSDTqgGqfiuTbT9YlgbJmE7eK3fpe107pJ6ixjPaCSkE7+UaYMOYmqmCsQSNbo045IVSScDrD6NeUjoQdCDexB0IuNo2k8P2dlPzuwBLVWWcQzU5YJZqUkkn7B6wOnXlVuk9rjcGH+ln9KOF2qzDfC6/5RJ+LpB6lx0907dx5babY5XhCELlWaQhCBCQhCBC+VL5TaxPpGtfjgzgcxzmOrCsk9ejYfUptQSrR2a/vFH9n3AOlld4nfnbj4ZZZYYlxGCkPyUopTAV8TqvZbHn7REafQ+7PTT8zMOKfmHnFOuOuG6lLUbqUT3JhurJMAGDmrc/h9ZbZ6h9oSDJmTe86n4D6qrYRZIivYSeURSMp2EVzQtaGM6rRsIXaNBHMIR4EuCQsSbAEnsIR7HKjLKqZtYzlKBSkkeJdUzNKFkMsgDnWfna3UqSOsfTQXENGpXCoqIqWJ087uFjRiSeQCtErgytTuF5zEbNPecoko+iXfnAPYQtYuB37XNrDmT3EWRKgoAjYxtjw7lbhzDmX6MHS9OacoYYUy7LOC/j8wPOpZ6rUSSVb3Ma7eILJOdyVxouUIU/Q50qep00b+0i+raj0WnQHvcHrotnpXQtDtd1Xt2r6U9v1ctK5vAQSWfqb/wDXMjbuJWL4QhCFWUkU7qTFRHS7HmC5uGOSoH0XEZO4Ys5HsmM0pGcdcH6CqJTJ1JsmwSgqHK76oOt/u83eMaPC6TFtm0jlI/3/AL2+UdY3FhBCjtpUcVdTvpphi1wwP73Go6rdy1NIety3IIuD0jtjAvBnmO5mNknRnJp3x6jSlKpcy4o+2rwwORSvMtlF/SM9RJ2OD2hw5rHNbSvoamSmk1YSPDzSEIR9JGkIQgQoffSQ4uNLy7w9h5lfK5Vqh4zqfvNsouB/GtB/diAEpEuPpLqmtePMHSXwM0912x7qcAuP4RERpRQtDDVnilK0zcmJsNkxYauxJ8fLBXRjpFa1FCwdBFa0oWhv5q0oSu+EI4UeUXO3UwJYFV0mlTdcqkpTqdLrnJ6acDbTKN1LVYAD5jy3MbMuHPI2UyWwkmXdaber88A5UpxAJCl6kNpJ+BNyBtqSethjHg74cjhWlsY3xBLIFZnW7yEs6klcm0bjnN/dWsdtkm2hUoRKyH2kg4Bxu1KzVf29RtCU2XRu9Uw9oj2nDl/aPmc+QK4CEg3CQD6R4POHKqm5vYQm6FUWkpUr7SUmuS65Z4D2XEn8bEdQSOunvYQ4EBwwKqSnnlpZmzwO4XtOII5ELT/jLB1Vy/xNP4frMsZeoSa+VwC5Sq+oWk9UqFiDp10BvFljY5xUcPYzYwwKpSmmU4npSFLYURyqmW/iYJA8rpv8XUAkxrmfacl33WXm1NOtqKFoWLFJBsQflEcnhMLsOS2Bde8UV4aIS5CVuTxsdx0Oo+I5L4jqXvrHbHS9oISqWlUr9rGLZN7RcHjpFumT7EfbU0zlS7+jYxcqWxpizDa13YnZNuebSfhcaVyLsPMOJ/gEbA41acBtRVI8SVGaSspTNScyyU/eHhFf5p/lG0uH+kdjF3LL994Wx2u57fba0/4/ZIQhCxQFIQhAha5PpLCU5tYWPwmk/wDtXf8AMRFSUcETA+k7pXhYqwRU9g9KTEvcdSlSVWP4LiGkq75wwVA9a5aZujKDZUGGxHzKv8u5cCK1tXaLTLORcG3IROHNWXC8K4p1B8tYkjwicPicwa6nFVdl0u4cp73Kyw6nSceBBtbYoSR7Xc6dFCMX5DZOVDOfGrVIl+ZmnyxS7UZwXJZaHQD7yiCADvrc+yY2g4Ww5T8K0OTo9NlESdPkmUMMsoTYJSBb8fM7k6neHCkp+M8btAq0v1er8sh/LqN3rnjMjVrT9zy2GeyurKeVtI7R9wAttpCHxZmSEIQIXy6OZsj/AEiFPGhw9mXcfzAw9LICFG9Xl2xygHb6wOm9gv15j1ibBF4pp6Tam5dxl1pDrTqShba0BSVg7hQ6jyPeOUsTZW8JT/Yds1FhVrayDlk4cnN5jy2OC02kiwI1BineVpGceKLIl3JvFiZuRaUcL1FZVJr1+wXYksqJ001KT1H7JjBDq7hXW2h8ojL2OjcWu1WwKK0ae06RlXTOxY4f9B6jQ9V0PLEWubWAN4q33LXi1TbvnH00ZJLUSZFZs4I0re4ocHqSbhKJoq9PqzkbYo1a/R7UtdU4jpV9NlIp9MmHVnexKQ3/AOf5xtKh7o/6fxWbL8PD7TaByYPq4/dIQhC5V6kIQgQoofSNYIXiPJNmtsI5n6BPtzKuUXJZcBaWPS6kH92Nacs5Ybxu3zBwfJ4/wfWsOz9/qtTlFyrnkFA2UPMHWNKGJMO1HA+KKrh+rslio02Ycln0dOZKiCR3B3B7EHrDTWMwcHbq6bj1/FTPpXHNpxHcf94+KrJV8R6nBeGaljrEtOoNHlzM1GedDTSNgOpUo9Egak9ADHiJR3mWEp1KtBYX1vGzvg74cxlNhY4grbA/pXVWgVpI1k2DZQaH6xsCrzCR8MJYYDM7Dkp9bN4Y7DozM7N5yaNzv3DU+HNZXySycp2S+C5SiSPI7Mauzk2lNlTLx3UfIbAdAB5xkOEIfwA0ABZgqKiWrmdPO7ic44k9UgTYXhFtrNal6NS5qem3UtSzCCtSz2Hbuew6x45zWNLnHABcWtLiGtGJKrFTjaVpQTZagSE3FyBa538x8xHahXOm9iPWIn1fNaq1HGzdeYdLYYWpEvLH3A1fVKhfUkb+du0SSwliuVxZQpeoyi08jg9ps+82rqk+kRmybwUtrSyRRZFpyx9objy5Zb5Plo2NUWbHHLJmHa9Dt4fdX+EIRKEwrzGYmX9MzLwrUKBWGEvyM43ym/vNqGqVp00UkgEHyjVHm3ltVcpcYztArKAX2SCxMpBCJho35Vpv0IGw2IIjcHGGOJnh/k88MCuyzPJL4jkQp2mzixoFm12121KFW17Gx6WKOogEo4hqFYN0byOsWo9BOfUvOf6T73n0z5LVDMvARa5l/eLhXqfN0KrTlNqEu5KT0o6pl6XdFltrSSCCPLaLIvxJl9DTSFOuOHkShAuSo6AetyNPw6wygK/KicOGIOSnf9GJghZ/phjJ5v2VqbpUsq29h4rp/m1/OJ6xifhlytOUOTuG8PPgCooZMxP8pH9pcPM4PQE8o/ZEZYiQQs4IwCsvW3W/mFoSzg5Y4DuGQ+mKQhCOyY0hCECEKQTsI17fSM5DGWnZfM+kMK8J4IlKuhsaIX7rLx7c2iD58ncxsJiPXGPnlR8pss5umvyktV6xXWXJWUps0AtpSSCFOup6oT07mw03HCcNMZ4lILBnqILQjNMOJxOBG4OvnjywUcuAfhoXXpyWzLxJKKEhLuf8nlFoul5YuC+q+6UnRPc3V8IjYc0gBsAp+YjB/Crn3Q838AsIlpZikVamNIlpqksaJaSkcqVNJ/wzaw7G6dxrnNKuYX/OCBrWxjhX1b9TV1Ne/wDGN4XNyDdhy88eeq5hCPlxwNJub/hHdR1FvNt35lpTbU3Nrf7sYjJnFmKcVVI02Qf5qVKr1UlVw+sac1+qRbT59o9nnhmSZBLlAprvLMupvNPIOrSdPY30J6+UYEioL3W9xk2bTHIfzn/Hz8N1Zl2bH4QK6cZ+yPv5eKWAv5x7LLHMB3A9b+0KlUyZKUTLdjcdlp8x/MXHQR42EVnS1UtFM2ogODm/vwPNT6op46qJ0MoxaVN6UnGZ1ht5h1D7LiQtDjagpKgdiCNxHfEesjcyDS5xGH6k6BJukqlXln3F9UX7HcefrEg0OeJewI9Y0jZFqRWtTCojyOhGx/eioq0rPks2oML9OR3C+o+HklTarb7x9wUeUEnpD0mpQr47OGVzFVLezEw5Lk1qRatUpNtHN9al0/3oHVaBbTqkHW4F8F8AuQ3/ABPzBOMaqyVYcw48C1zAcsxOWSpCL9eS4WbdSgbExPzPbOWhZM4MerVWJmJgXRJ05tQDs270SnyG5PQC/YHCHBFxGU3H8hPYOmqbT8P1mVeenZWVpzYaZmWVuKWrlTc+0gq1HUEHvZA6OP04OKsOlr7V/IZAxhLG5B2zTrh3aY8seil0lCU7AD0jmEIXqvEhCECEhCKedmBLNF1SuVKEqUba6Aa6dYELymbGadHyewVU8TV15LUlJoHKi/tvuHRLaR1Uo/6nYGNRGZeZFYzhx1UcU1xYVNTK/smUq5m5doE8jSL9ACNdLkk2j3PFPxGTXEFj1TcotbOEKStTVOZcuPHVsX1D7yug6JHmYxNLtQyVM3pDwjQLQNz7AFBF+KmHrH/Ibd+69Pl5jmt5aYllK9QZxUrPy+gB9pDqbWKFj4kkaEfjvGzrh/4mKHnhRQlot07EUs2FTlLeVZWvxt31Wgnr02OsaqkAo1Ha0VlKq05RKgxPSE0/IzrCudqZl3C24g90qGoMcoZ3QncKS2/dmltyIE9mUaO+x3HzGoW7FRsm4jwuaWYbWCqKPCUhdTmQpMs0e/VZ7AX/AJiIt5IceczOJbo2PJRyZmQizVYkG9XCBoXWxoL/AHk6fqxWYixk7jyrv1V55DpcsEIbNw0jcJ3/APpvDLeO320FNwU59Y/T9I379v8ASp2kulWU9bwV7MGNzxGYdth03xwPTNUExMvTr7kxMOKdedUVrWrck63MfEOtusNheKFJJJJVmgBowCQjjmHcQuB1j5xXq5SAlYKfZOgBBsRbbXpEksmcyv6TU4UuedT+lpZIsVCxfbGgVbuNAfn1iNpHQj8DFTT6xM4en5eoyr31aZl1c7bitB6Hy7jteJDYlrSWRVCVubDk4bjzHLyJTLa1mMtSnMRycM2nY+RU20HmSD+UYzzpz3w/kthtU9Wng5OvAplKcyR40wvsB0TfdRFhfvpGBs2+PFrDlJl5HDFMXMV11u701NaS0urX3Be7hv6AdztEIMV4trGNa3MVau1J+rVF88y5iYNz5ADQAdgAAO0aBNfHJGHwHHEYgqN2Fcaqq5BLaI4Ixy9p3kOuu26u2cGalfzjxU/W669dRu3Lyrdw1LN30QgHz3J1J1jxdFrlRwjiGQrtImVyVTkXkvy8w3oUKB/Ii4I6gkdY7jr5xSzDYPTSG3iJPEdVeT6KCOAU8bAGAYYYZYbLbZw3Z/SGf+A2KswhqVq0sQxU5FKtWHgNwN+RWpST003BjLcaX8ls56vkFmDKYmpvNMS+jVRkSohMwwT7SfUWuk9CCO8bh8IYilcWYdp1ZkVOqk5+WbmmfHQUL5Fp5k3SdQbGHunm9K3PULM95LFNj1XY/pu06bj4fRXmEIQrURSOqYZLvJYgWN47YQIUEOL7g1/rk5jvAkkOZRLtUo7CT7ZNyp9pI9bqQN9wLk3hWym2h0VtY73jd+phKlKJJ13iKHEnwWyOPnJrEuC0M0rESruTEiSEy82rqR9xw667Hra5MNtRTY9uNXBdW97afhorSPZ9l+3R3TY8ufTXsdhBKSuwT7RJtYb3i44gw9UsK1eZpVYkZim1OXVyOy0y2UKQb+e4PQjQjUR6PAmGQ++iemW/ZB5WknofvGI7V1TKSIyP/ZV6+lbwB7TiF6DA+FDT2UvutD6w6Oa52SntGSZALlUjw1qQBsAYopCWShI022i52HKPKKoqZ3VMhkkzJTLM/jJxVxark02kFSg4OxFo+ncYNy3vyv8ACq8WWYmA0nfWLllnl7P5t4wapMopTMm1Zydm7GzbQte3ZR2A9d7GE8FCKuURRtxccgm2dtNTxOqJuy1oxJXpZBupVTA89ixmmOqpEm6GlrB9o/eWB1Sk2BPc9RciwMYzamdEMH1K7RO2jYYp1FoMvRpWUabpjLAYTLcg5Si1iCDvfW99yTeIT565SP5TYoD0mCvD0+smVXqfAV1ZUe43Hlf7pMSu1rqsoKds8fa97XXcdOX/AFQmwreprWqpKeRvCScWZ6jY9ef/ABWxyvPPAhCUM/si5i1T5dmknxHFKv8AraR0ScyHBe+sVSlXEQ5sbYzkFP2xtjPZCx/jDCyKpKqQLIdQbtrt18/KMPTEu5KvKadSUuJNlJO4iSc7LJcTqIxfj3DXjIVNso/rDfvhPxpH+sTGxbS9C4QSnsnToU7082PZKxyDaOp5PPzW6AkxVyclMVGcYk5OXenJp8hDbLCCta1nZISASSdtIm7w18FCKa5LYlzDl0PTKCl2VoRsUtq3Cn+ijtZGw5dbnQWLFG6Y4NTfbNs0ljwGWpdnyaNT3fc6BeK4SODtWL52TxjjiSH6EQfFkKVMIt9cOlnHE/4elwPj3Ps2vsIlZZMq3yISlKAAAEiwAEctyqG+TlFgkaDoI7YfoomxN4WrMNr2tUWxUmonyHIcgP3qeaQhCOqZFypJSog7g2jiLjV5ItOl5IuhZ18jFugQkcciSLcot6RzCBCx3m7kbhLOOmplq/S0uTKBZmoS4CJlg/qr7fqm4PbtFPG/Cni7ATq3KQyrEtJSPZXKJ5X2x2U3ufVJMTwhDPaNlU9pNwlyO4Uqsm8lfZHYidxR+67MfDmPh8VrJZqK5da2nm1NOoVyqQsWUk9iDFcKmkt3Nh53ie2LspcMY6QDWqLKTb9rCYKSl0DtzpIUfS8YXxRwUSD7jjuHMQzFP5rn6tPNh5HkApPKQB58x84ryqupVx5wkPHgfnl81aFHfWzanAVIMZ8R4jP5BRqk5WbxPWZOk01ozM/OOBplpBI1IJJJ7AA+QGvSJ4ZPZZSmV2F5elspS7NK+1m5sIt4ztrHz5RawB2HmTHkMheHYZUuTtSqsxL1OuP/AGbb7QPKy1e9k3F7qIFz5Ad75uiVXfsb8AwzTj1h+Q8yoTeu8LbSeKSkd6lup94+Q5dc9lwEgbAR5zHeDJDHmHJ6i1JnnlplHKFBPtNq+FST0IOvz7x6SES57GyNLHjEFV/HI+F4kjODhmDsVrixjhSo5aYpmqHVCC4yq7TwFkvtm/K4nyI6dCDFGmpJ5SLgEbi+oia+duSrWbWF0y6VsytalFc8nNuJJSnXVCralJAH4gGMT4a4JXrpOIsUKcaHvMU5nlJ/fXcD+GKnrbsVIqSymbiw6HEZdCr4s++FnzUYkrn8MoyIwJxO4wGh+XzUdZmsoAsFA+hj1+DOHvGOZz7K25FVKpajcz9QSWwE9eRFuZR/l5jeJgYPyDwXghxp6QojD023Ypm5wl9wHuCq4SfQCMhIaCLAaAdBDxQ3Tawh1W/HoPPy8UwWhfvIss6PD9Tvs0YjxJ7liXJfhrwjk+HJuTkU1CuO/wDUqs22ku9bhsbNp8k79SYy5yJB90fKOYRP442xNDGDABVbVVc9dKZ6l5c48z+/kkIQjokiQjm0IEL083/ZXf2T+UeXhCBCQhCBCQhCBCQhCBCQhCBCQhCBCQhCBCQhCBCQhCBCQhCBCv8ATf7E16H84QhAhf/Z"""
b64_logo = B64_ATLAS_LOGO

# Fallback: intentar cargar archivo local si existe (prioridad al archivo)
try:
    for logo_path in ["logo_atlas.png", "image_c93c8b.png", "atlas_logo.png"]:
        try:
            with open(logo_path, "rb") as f:
                b64_logo = base64.b64encode(f.read()).decode()
                break
        except:
            continue
except:
    pass

st.markdown("""
<style>
    html, body { font-family: Inter, sans-serif; }
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .glass { background: rgba(255,255,255,0.95) !important; border-radius: 18px; padding: 20px 22px; box-shadow: 0 8px 32px rgba(15,23,42,0.08); border: 1px solid white; }
    .glass-dark { background: rgba(15,23,42,0.88) !important; color: white; border-radius: 18px; padding: 16px 18px; }
    .badge { display:inline-flex; padding:7px 14px; border-radius:100px; font-size:0.82rem; font-weight:800; letter-spacing:0.3px; }
    .badge-ok { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
    .badge-warn { background:#fef9c3; color:#854d0e; border:1px solid #fde68a; }
    .badge-orange { background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; }
    .badge-red { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }
    .filter-pill { background: white; border: 1px solid #e2e8f0; border-radius: 50px !important; padding: 10px 18px 12px 18px !important; }
    .filter-label { font-size:0.72rem !important; font-weight:800 !important; color:#64748b !important; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:2px; }
    .rep-box { background:#f1f5f9; border:1px solid #e2e8f0; border-radius:8px; padding:4px 10px; font-weight:700; font-size:0.85rem; display:inline-flex; gap:6px; align-items:center; }
</style>
""", unsafe_allow_html=True)

SHEET_ID_PRUEBAS = "12uBzVEE5ZqO7V6OIKSlCTB7BdSQWk_3sn12LhFdMWg4"

def norm(s):
    return str(s).strip().upper().replace("  "," ").replace("\n","").replace("\r","")

@st.cache_data(ttl=20, show_spinner=False)
def cargar_datos(sheet_id_override=None):
    df_privado = None
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
            client = gspread.authorize(creds)
            sid = sheet_id_override or st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            if sid:
                sh = client.open_by_key(sid)
                ws = None
                for name_try in ["BDSUCURSALES2", "BDSUCURSALES"]:
                    try:
                        ws = sh.worksheet(name_try)
                        break
                    except:
                        continue
                if not ws:
                    ws = sh.sheet1
                data = ws.get_all_records()
                if data and len(data) > 0:
                    df_tmp = pd.DataFrame(data)
                    df_tmp.columns = df_tmp.columns.str.strip().str.upper()
                    df_tmp = df_tmp.dropna(how='all')
                    if len(df_tmp) >= 1:
                        df_privado = df_tmp
    except:
        pass
    if df_privado is not None and not df_privado.empty and len(df_privado) > 5:
        return df_privado
    try:
        base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTySrWdMEtPBo7u4r6df8shaedXk8783RUOdOPsjLwIh1xz4nLHdAdaheYFMB1-CLI2XtzpzLa7SQXm/pub?output=csv"
        url = f"{base_url}&cb={int(time.time())}"
        df = pd.read_csv(url, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        return df.dropna(how='all')
    except Exception as e:
        if df_privado is not None:
            return df_privado
        return pd.DataFrame(columns=["ESTADO","SUCURSAL","TELMEX","NO. REPORTE","FECHA","OBSERVACIONES"])

def deduplicar_df(df_in):
    try:
        import unicodedata
        def clean_norm(s):
            s = str(s).strip()
            if not s:
                return ""
            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            s = s.upper()
            s = re.sub(r'\s+', ' ', s)
            return s.strip()
        if df_in is None or df_in.empty:
            return df_in
        col_est = None
        col_suc = None
        for c in df_in.columns:
            cu = str(c).upper()
            if not col_est and ('ESTADO' in cu or cu == 'EDO'):
                col_est = c
            if not col_suc and 'SUCURSAL' in cu:
                col_suc = c
        if not col_est or not col_suc:
            return df_in
        df_in['_KEY_DEDUP'] = df_in[col_est].apply(clean_norm) + "||" + df_in[col_suc].apply(clean_norm)
        col_rep = None
        for c in df_in.columns:
            if 'REPORTE' in str(c).upper():
                col_rep = c
                break
        if col_rep:
            df_in['_HAS_REP'] = df_in[col_rep].apply(lambda x: 1 if str(x).strip().lower() not in ["", "0", "0.0", "sin reporte", "none", "nan", "vacio", "s/r"] else 0)
            df_in = df_in.sort_values(by=['_KEY_DEDUP', '_HAS_REP'])
        df_in = df_in.drop_duplicates(subset=['_KEY_DEDUP'], keep='last')
        df_in = df_in.drop(columns=[c for c in ['_KEY_DEDUP', '_HAS_REP'] if c in df_in.columns])
        return df_in
    except Exception as e:
        return df_in

df_raw = cargar_datos()

def buscar_col_temp(kws, df_ref):
    for c in df_ref.columns:
        for kw in kws:
            if kw in c: return c
    return None

COL_EST_TMP = buscar_col_temp(['ESTADO','EDO'], df_raw)
COL_SUC_TMP = buscar_col_temp(['SUCURSAL','SUC','SITIO'], df_raw)

if COL_EST_TMP and not df_raw.empty:
    df_raw[COL_EST_TMP] = df_raw[COL_EST_TMP].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
if COL_SUC_TMP and not df_raw.empty:
    df_raw[COL_SUC_TMP] = df_raw[COL_SUC_TMP].astype(str).str.strip()

df = deduplicar_df(df_raw)

def buscar_col(kws):
    for c in df.columns:
        for kw in kws:
            if kw in c: return c
    return None


COL_EST = buscar_col(['ESTADO','EDO'])
COL_SUC = buscar_col(['SUCURSAL','SUC','SITIO'])
COL_TEL = buscar_col(['TELMEX','TEL','LINEA'])
COL_REP = buscar_col(['NO. REPORTE','NO REPORTE','REPORTE'])
COL_FEC = buscar_col(['FECHA','FEC'])
COL_OBS = buscar_col(['OBSERVACIONES','OBS','FALLA','COMENTARIO'])

if COL_EST and not df.empty:
    df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
if COL_SUC and not df.empty:
    df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Sin fecha"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, "Fecha invalida"
    diff = (datetime.now() - dt).days
    if diff < 0:
        return diff, "Fecha futura"
    if diff == 0:
        return diff, "Hoy"
    elif diff == 1:
        return diff, "1 dia"
    elif diff <= 2:
        return diff, f"{diff} dias"
    elif diff <= 5:
        return diff, f"{diff} dias"
    else:
        return diff, f"{diff} dias - Critico"

def split_tels(raw):
    if pd.isna(raw) or str(raw).lower() in ['nan','none','']: return []
    s = str(raw).strip()
    s = re.sub(r'(\d{3})(\d{3}-\d{3}-\d{4})', r'\1,\2', s)
    s = re.sub(r'(\d{4})(\d{3}-)', r'\1,\2', s)
    partes = re.split(r'[\n,;/\s]+', s)
    tels = []
    for p in partes:
        p = p.strip()
        if not p or p.lower()=='nan': continue
        if re.match(r'^\d{3}-\d{3}-\d{4}$', p):
            tels.append(p)
        elif re.match(r'^\d{10}$', p):
            tels.append(f"{p[:3]}-{p[3:6]}-{p[6:]}")
        elif '-' in p and len(p)>=7:
            tels.append(p)
    if not tels:
        raw_tels = [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']
        for item in raw_tels:
            encontrados = re.findall(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}|\d{10}', item)
            if encontrados:
                for e in encontrados:
                    e = e.replace(' ', '-')
                    if len(e)==10 and '-' not in e:
                        e = f"{e[:3]}-{e[3:6]}-{e[6:]}"
                    tels.append(e)
            else:
                tels.append(item)
    seen=set(); uniq=[]
    for t in tels:
        if t not in seen:
            seen.add(t); uniq.append(t)
    return uniq

USUARIOS = {"yair": "AtlasY", "francisco": "AtlasF"}

def check_login(user, pwd):
    try:
        if "users" in st.secrets:
            users_secret = st.secrets["users"]
            return user in users_secret and users_secret[user] == pwd
        else:
            return USUARIOS.get(user) == pwd
    except:
        return USUARIOS.get(user) == pwd

def log_acceso(usuario, accion="Login"):
    now = datetime.now()
    fecha = now.strftime("%d/%m/%Y")
    hora = now.strftime("%H:%M:%S")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("LOG_ACCESOS")
            except:
                ws = sh.add_worksheet(title="LOG_ACCESOS", rows=1000, cols=10)
                ws.append_row(["FECHA", "HORA", "USUARIO", "ACCION", "DETALLE"])
            ws.append_row([fecha, hora, usuario, accion, "Acceso desde app"])
    except:
        pass

def log_reporte_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, tel="", observaciones=""):
    now = datetime.now()
    fecha_reg = now.strftime("%d/%m/%Y")
    hora_reg = now.strftime("%H:%M:%S")
    mes = now.strftime("%m")
    anio = now.strftime("%Y")
    dia = now.strftime("%d")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, no_reporte, fecha_reporte, tel, observaciones])
            return True
    except Exception as e:
        return False
    return True

def log_eliminacion_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, observaciones=""):
    # Registra la eliminacion en HISTORIAL_REPORTES como evento ELIMINADO, pero mantiene historial
    now = datetime.now()
    fecha_reg = now.strftime("%d/%m/%Y")
    hora_reg = now.strftime("%H:%M:%S")
    mes = now.strftime("%m")
    anio = now.strftime("%Y")
    dia = now.strftime("%d")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, f"ELIMINADO-{no_reporte}", fecha_reporte, "", f"ELIMINACION: {observaciones}"])
            return True
    except Exception as e:
        return False
    return True

def eliminar_reporte_hoja1(estado, sucursal, no_reporte_actual):
    # Limpia NO_REPORTE, FECHA_DE_REPORTE y FALLA en BDSUCURSALES2, con ffill de ESTADO para celdas combinadas
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            import unicodedata
            def clean_norm(s):
                s = str(s).strip()
                if not s:
                    return ""
                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                s = s.upper()
                s = re.sub(r'\s+', ' ', s)
                return s.strip()
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            ws_main = None
            for name_try in ["BDSUCURSALES2", "BDSUCURSALES"]:
                try:
                    ws_main = sh.worksheet(name_try)
                    break
                except:
                    continue
            if not ws_main:
                ws_main = sh.sheet1
            headers = ws_main.row_values(1)
            headers_upper = [h.strip().upper() for h in headers]
            def find_idx(kws):
                for i, h in enumerate(headers_upper):
                    for kw in kws:
                        if kw in h:
                            return i+1
                return None
            col_est_idx = find_idx(['ESTADO','EDO'])
            col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO'])
            col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
            col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA','FEC'])
            col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])
            all_vals = ws_main.get_all_values()
            row_found = None
            last_estado = ""
            for idx_row in range(1, len(all_vals)):
                row = all_vals[idx_row]
                try:
                    est_cell_raw = row[col_est_idx-1] if col_est_idx and col_est_idx-1 < len(row) else ""
                    suc_cell_raw = row[col_suc_idx-1] if col_suc_idx and col_suc_idx-1 < len(row) else ""
                    # ffill ESTADO: si esta vacio, usa el ultimo estado no vacio
                    if est_cell_raw and str(est_cell_raw).strip():
                        last_estado = est_cell_raw
                    est_cell = last_estado if last_estado else est_cell_raw
                    if not est_cell or not suc_cell_raw:
                        continue
                    if clean_norm(est_cell) == clean_norm(estado) and clean_norm(suc_cell_raw) == clean_norm(sucursal):
                        row_found = idx_row+1
                        break
                except:
                    continue
            if row_found:
                if col_rep_idx: ws_main.update_cell(row_found, col_rep_idx, "")
                if col_fec_idx: ws_main.update_cell(row_found, col_fec_idx, "")
                if col_falla_idx: ws_main.update_cell(row_found, col_falla_idx, "")
                return True, row_found
            else:
                return False, f"No se encontro: {estado} / {sucursal} en {ws_main.title} (buscadas {len(all_vals)} filas, ffill aplicado)"
        else:
            return True, "Modo demo - simulado"
    except Exception as e:
        return False, str(e)

lista_estados = sorted(df[COL_EST].dropna().unique()) if COL_EST in df.columns else []
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP and COL_REP in df.columns else pd.DataFrame()

for k in ['admin_auth','show_login','show_add_form','current_user','batch_reportes','show_close_login','show_close_confirm','close_target','close_auth','close_user','last_logged_suc','last_visita_log','visitas_demo','filtro_activo_sel','show_delete_login','show_delete_confirm','delete_target','delete_auth']:
    if k not in st.session_state:
        st.session_state[k] = False if 'auth' in k or 'show' in k else ([] if 'batch' in k or 'visitas' in k or 'demo' in k else None)
if 'visitas_demo' not in st.session_state: st.session_state['visitas_demo']=[]
if 'batch_reportes' not in st.session_state: st.session_state['batch_reportes']=[]
if 'filtro_activo_sel' not in st.session_state: st.session_state['filtro_activo_sel']="-- Ver todas las sucursales --"

# --- PREPARAR OPCIONES REPORTES ACTIVOS ---
opciones_activas = []
mapa_activos = {}
mapa_activos_global = {}
if not df_reportes.empty:
    for _, row in df_reportes.iterrows():
        estado = str(row.get(COL_EST, "")).strip()
        suc = str(row.get(COL_SUC, "")).strip()
        rep = str(row.get(COL_REP, "")).strip()
        fec = str(row.get(COL_FEC, "")).strip()
        dias, txt_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin fecha")
        label = f"{suc} - {estado} | REP: {rep} | {txt_dias}"
        opciones_activas.append(label)
        mapa_activos[label] = {"estado": estado, "sucursal": suc, "row": row}
    opciones_activas = sorted(opciones_activas)
    mapa_activos_global = mapa_activos
opciones_con_todos = ["-- Ver todas las sucursales --"] + opciones_activas

# HEADER - c1 titulo, c2 reportes + filtro mismo tamaño que negro, sin boton Limpiar, automatico
c1, c2 = st.columns([2.2, 1.3])
with c1:
    if b64_logo:
        st.markdown(f"""<div style="display:flex; align-items:center; gap:16px"><div style="width:52px; height:52px; border-radius:14px; overflow:hidden; background:white"><img src="data:image/png;base64,{b64_logo}" style="width:100%; height:100%; object-fit:cover"></div><div style="font-size:2rem; font-weight:900; letter-spacing:-0.8px">SUCURSALES - PRUEBAS</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="font-size:2rem; font-weight:900;">SUCURSALES - PRUEBAS</div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="glass-dark"><div style="display:flex; justify-content:space-between; align-items:center"><div style="display:flex; gap:10px; align-items:center"><div style="width:34px; height:34px; background:rgba(239,68,68,0.25); border-radius:9px; display:flex; align-items:center; justify-content:center">🚨</div><div><div style="font-weight:700">Reportes Activos</div><div style="font-size:0.75rem; opacity:0.7">{len(df_reportes)} requieren atencion</div></div></div><div style="font-size:1.6rem; font-weight:900">{len(df_reportes)}</div></div></div>""", unsafe_allow_html=True)
    if not df_reportes.empty:
        st.markdown(f"""
        <div class="glass" style="margin-top:10px; padding:10px 14px; border-left:4px solid #ef4444; background:white !important; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:6px;">
                    <div style="width:18px; height:18px; background:#ef4444; border-radius:5px; display:flex; align-items:center; justify-content:center; color:white; font-size:10px;">🚨</div>
                    <div style="font-weight:800; font-size:0.68rem; letter-spacing:0.4px; color:#991b1b;">VER SOLO SUCURSALES CON REPORTE ACTIVO</div>
                </div>
                <span class="badge badge-red" style="font-size:0.65rem; padding:3px 8px;">{len(df_reportes)} encontradas</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        default_idx_activo = 0
        if st.session_state.get('filtro_activo_sel') in opciones_con_todos:
            default_idx_activo = opciones_con_todos.index(st.session_state['filtro_activo_sel'])
        sel_activo = st.selectbox(
            "Filtro reporte activo",
            opciones_con_todos,
            index=default_idx_activo,
            key="filtro_activo_sel",
            label_visibility="collapsed",
            placeholder="🔍 Selecciona sucursal con reporte activo..."
        )
        if sel_activo != "-- Ver todas las sucursales --":
            info_sel = mapa_activos.get(sel_activo)
            if info_sel:
                if st.session_state.get('estado_real') != info_sel['estado'] or st.session_state.get('sucursal_real') != info_sel['sucursal']:
                    st.session_state['estado_real'] = info_sel['estado']
                    st.session_state['sucursal_real'] = info_sel['sucursal']
                    st.rerun()
    else:
        st.markdown('<div class="glass" style="margin-top:10px; padding:10px 14px; border-left:4px solid #16a34a; background:white !important; border-radius:12px;"><div style="display:flex; align-items:center; gap:8px;"><div style="width:20px; height:20px; background:#16a34a; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px;">✅</div><b style="color:#166534; font-size:0.75rem;">Sin reportes activos</b></div></div>', unsafe_allow_html=True)

es_modo_agregar = st.session_state.get('show_add_form', False) and st.session_state.get('admin_auth', False)

default_est_idx = 0
default_suc = None
if 'estado_real' in st.session_state and st.session_state['estado_real'] in lista_estados:
    default_est_idx = lista_estados.index(st.session_state['estado_real'])
    default_suc = st.session_state.get('sucursal_real')

if not es_modo_agregar:
    f1, f2, f3 = st.columns([1.1, 1.8, 0.7], gap="medium")
    with f1:
        st.markdown('<div class="filter-pill"><div class="filter-label">📍 Estado</div>', unsafe_allow_html=True)
        estado_actual = st.selectbox("Estado", lista_estados, index=default_est_idx, key="estado_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    with f2:
        st.markdown(f'<div class="filter-pill"><div class="filter-label">🏬 Sucursales • {len(lista_suc)} en {estado_actual}</div>', unsafe_allow_html=True)
        idx_suc = lista_suc.index(default_suc) if default_suc and default_suc in lista_suc else 0
        sucursal_actual = st.selectbox("Sucursales", lista_suc, index=idx_suc, key="sucursal_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="filter-pill"><div class="filter-label">⚡ Acciones</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("🔄", use_container_width=True, help="Actualizar"):
                st.cache_data.clear()
                st.rerun()
        with ca2:
            if st.button("➕", use_container_width=True, help="Agregar reporte"):
                st.session_state['show_login'] = True
                st.session_state['show_add_form'] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Guardar estado actual como prev para la proxima corrida (para detectar cambio manual)
    st.session_state['prev_estado_real'] = st.session_state.get('estado_real')
    st.session_state['prev_sucursal_real'] = st.session_state.get('sucursal_real')
else:
    estado_actual = st.session_state.get('estado_real', lista_estados[0] if lista_estados else "")
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    sucursal_actual = st.session_state.get('sucursal_real', lista_suc[0] if lista_suc else "")

# LOGIN
if st.session_state['show_login'] and not st.session_state['admin_auth']:
    st.markdown('<div class="glass" style="border:2px solid #0f172a; padding:24px">', unsafe_allow_html=True)
    st.markdown("### 🔐 Login Administrador")
    u = st.text_input("Usuario", placeholder="Ingresa tu usuario", key="login_user")
    p = st.text_input("Contraseña", type="password", key="login_pwd")
    cl1, cl2 = st.columns(2)
    with cl1:
        if st.button("Ingresar", type="primary", use_container_width=True):
            if check_login(u.lower().strip(), p):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = u.lower().strip()
                st.session_state['show_login'] = False
                st.session_state['show_add_form'] = True
                log_acceso(u.lower().strip(), "Login exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    with cl2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state['show_login'] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# FORMULARIO
if st.session_state['admin_auth'] and st.session_state['show_add_form']:
    st.markdown('<div class="glass" style="border:2px solid #16a34a; padding:28px">', unsafe_allow_html=True)
    st.markdown(f"### ➕ Agregar Reporte - Usuario: **{st.session_state['current_user']}** - PRUEBAS REALES")
    st.info(f"Hoja pruebas ID: {SHEET_ID_PRUEBAS[:20]}... | Modo lote: agrega N reportes y al final guarda todo")
    st.markdown("#### 1⃣ Selecciona Estado y Sucursal")
    fc_sel1, fc_sel2 = st.columns(2)
    with fc_sel1:
        est_new = st.selectbox("Estado del reporte", lista_estados, index=lista_estados.index(estado_actual) if estado_actual in lista_estados else 0, key="form_est_outside")
    est_new_clean = str(est_new).strip().upper()
    df_suc_filtro = df[df[COL_EST].str.strip().str.upper() == est_new_clean] if COL_EST else df
    lista_suc_filtro = sorted(df_suc_filtro[COL_SUC].dropna().unique()) if COL_SUC else []
    with fc_sel2:
        opciones_suc = lista_suc_filtro + ["➕ Otra / Nueva sucursal..."]
        idx_def = lista_suc_filtro.index(sucursal_actual) if sucursal_actual in lista_suc_filtro else 0
        suc_sel = st.selectbox(f"Sucursal - {len(lista_suc_filtro)} en {est_new_clean}", opciones_suc, index=idx_def, key=f"form_suc_outside_{est_new_clean}")
    if suc_sel == "➕ Otra / Nueva sucursal...":
        suc_new = st.text_input("Escribe nueva sucursal *", placeholder="Ej: CORDOBA", key="form_suc_new_text")
        lineas_sucursal = []
    else:
        suc_new = suc_sel
        fila_suc = df_suc_filtro[df_suc_filtro[COL_SUC] == suc_new] if COL_SUC else pd.DataFrame()
        if not fila_suc.empty:
            lineas_sucursal = split_tels(fila_suc.iloc[0].get(COL_TEL, ""))
        else:
            lineas_sucursal = []
    st.markdown("---")
    st.markdown("#### 2⃣ Lineas con falla")
    if lineas_sucursal:
        cols_lineas = st.columns(2)
        seleccionadas = []
        for i, linea in enumerate(lineas_sucursal):
            with cols_lineas[i % 2]:
                if st.checkbox(f"{linea}", key=f"chk_linea_{est_new}_{suc_new}_{i}"):
                    seleccionadas.append(linea)
        if seleccionadas:
            st.info(f"Con falla: {', '.join(seleccionadas)}")
        tel_extra = st.text_input("¿Otra linea no listada? (opcional)", placeholder="551-999-8888", key="tel_extra_outside")
        if tel_extra:
            seleccionadas.append(tel_extra)
        tel_final = ", ".join(seleccionadas)
    else:
        st.info("Sin lineas registradas o sucursal nueva")
        tel_final = st.text_input("Lineas con falla", placeholder="551-102-2050", key="tel_new_suc_outside")
        seleccionadas = [tel_final] if tel_final else []
    st.markdown("---")
    st.markdown("#### 3⃣ Datos del reporte")
    st.markdown(f"**Resumen:** Estado: {est_new} | Sucursal: {suc_new} | Lineas: {tel_final if tel_final else 'Ninguna'}")
    with st.form("form_reporte_final", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            rep_new = st.text_input("No. Reporte *", placeholder="45163", key="form_rep_final")
        with fc2:
            fec_new = st.date_input("Fecha Reporte", value=datetime.now().date(), max_value=datetime.now().date(), key="form_fec_final")
        obs_new = st.text_area("📝 Observaciones / Falla reportada *", placeholder="Ej: falla, sin linea, ruido...", height=90, key="form_obs_final")
        st.markdown("---")
        c1f, c2f = st.columns([0.7, 1.3])
        with c1f:
            btn_close = st.form_submit_button("Cerrar formulario", use_container_width=True)
        with c2f:
            btn_add = st.form_submit_button("➕ AGREGAR REPORTE A LA LISTA", type="primary", use_container_width=True)
        if btn_close:
            log_acceso(st.session_state['current_user'], "Cerro formulario y logout")
            st.session_state['admin_auth'] = False
            st.session_state['show_add_form'] = False
            st.session_state['show_login'] = False
            st.session_state['current_user'] = None
            st.session_state['batch_reportes'] = []
            st.rerun()
        if btn_add:
            rep_new_clean = str(rep_new).strip()
            try:
                reportes_activos_existentes = [str(r).strip() for r in df[COL_REP].dropna().tolist() if tiene_reporte(r)] if COL_REP in df.columns else []
            except:
                reportes_activos_existentes = []
            try:
                reportes_en_cola = [str(r['no_reporte']).strip() for r in st.session_state.get('batch_reportes', [])]
            except:
                reportes_en_cola = []
            if not rep_new_clean:
                st.error("No. Reporte obligatorio")
            elif not rep_new_clean.isdigit():
                st.error("❌ Solo numeros")
            elif rep_new_clean in reportes_activos_existentes:
                st.error(f"❌ El reporte {rep_new_clean} ya existe como ACTIVO")
            elif rep_new_clean in reportes_en_cola:
                st.error(f"❌ Ya esta en la cola")
            elif not suc_new:
                st.error("Sucursal obligatoria")
            elif not tel_final:
                st.error("Selecciona al menos una linea")
            elif not obs_new:
                st.error("Observaciones obligatoria")
            elif fec_new > datetime.now().date():
                st.error("❌ Fecha futura no permitida")
            else:
                nuevo = {"estado": est_new, "sucursal": suc_new, "tel": tel_final, "no_reporte": rep_new_clean, "fecha_reporte": fec_new.strftime("%d/%m/%Y"), "obs": obs_new}
                st.session_state['batch_reportes'].append(nuevo)
                st.success(f"✅ Reporte {rep_new_clean} agregado - Total: {len(st.session_state['batch_reportes'])}")
                st.session_state['clear_after_add'] = True
                st.rerun()
    if st.session_state.get('clear_after_add'):
        for k in list(st.session_state.keys()):
            if k.startswith("chk_linea_"):
                del st.session_state[k]
        for k in ["form_rep_final", "form_obs_final", "tel_extra_outside", "tel_new_suc_outside"]:
            if k in st.session_state:
                try:
                    del st.session_state[k]
                except:
                    pass
        st.session_state['clear_after_add'] = False
        st.rerun()
    if st.session_state['batch_reportes']:
        st.markdown("---")
        st.markdown(f"#### 📋 Reportes en cola ({len(st.session_state['batch_reportes'])}) - Aun no guardados")
        for idx, r in enumerate(st.session_state['batch_reportes']):
            col_r1, col_r2 = st.columns([5,1])
            with col_r1:
                st.markdown(f"<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #16a34a; padding:10px 14px; border-radius:10px; margin-bottom:8px'><b>{idx+1}. {r['sucursal']} ({r['estado']})</b> - REP: {r['no_reporte']} - Lineas: {r['tel']}<br><small>{r['obs'][:100]}</small></div>", unsafe_allow_html=True)
            with col_r2:
                if st.button("❌", key=f"del_batch_{idx}_{r['no_reporte']}"):
                    st.session_state['batch_reportes'].pop(idx)
                    st.rerun()
        st.markdown("---")
        c_save1, c_save2 = st.columns([0.5, 1.5])
        with c_save1:
            if st.button("🗑 Limpiar lista", use_container_width=True):
                st.session_state['batch_reportes'] = []
                st.rerun()
        with c_save2:
            if st.button(f"💾 GUARDAR LOS {len(st.session_state['batch_reportes'])} REPORTES EN GOOGLE SHEETS (PRUEBA REAL)", type="primary", use_container_width=True):
                try:
                    guardados = 0
                    if "gcp_service_account" in st.secrets:
                        import gspread
                        from google.oauth2.service_account import Credentials
                        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
                        client = gspread.authorize(creds)
                        sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
                        sh = client.open_by_key(sheet_id)
                        try:
                            ws_main = sh.worksheet("BDSUCURSALES")
                        except:
                            try:
                                ws_main = sh.worksheet("BDSUCURSALES2")
                            except:
                                ws_main = sh.sheet1
                        headers = ws_main.row_values(1)
                        headers_upper = [h.strip().upper() for h in headers]
                        def find_idx(kws):
                            for i, h in enumerate(headers_upper):
                                for kw in kws:
                                    if kw in h:
                                        return i+1
                            return None
                        col_est_idx = find_idx(['ESTADO','EDO'])
                        col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO'])
                        col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
                        col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA','FEC'])
                        col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])
                        col_tel_idx = find_idx(['TELMEX','TEL','LINEA'])
                        all_vals = ws_main.get_all_values()
                        for r in st.session_state['batch_reportes']:
                            row_found = None
                            last_estado_g = ""
                            import unicodedata
                            def clean_norm_g(s):
                                s = str(s).strip()
                                if not s:
                                    return ""
                                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                                s = s.upper()
                                s = re.sub(r'\s+', ' ', s)
                                return s.strip()
                            for idx_row in range(1, len(all_vals)):
                                row = all_vals[idx_row]
                                try:
                                    est_raw = row[col_est_idx-1] if col_est_idx and col_est_idx-1 < len(row) else ""
                                    suc_raw = row[col_suc_idx-1] if col_suc_idx and col_suc_idx-1 < len(row) else ""
                                    if est_raw and str(est_raw).strip():
                                        last_estado_g = est_raw
                                    est_cell = last_estado_g if last_estado_g else est_raw
                                    if clean_norm_g(est_cell) == clean_norm_g(r['estado']) and clean_norm_g(suc_raw) == clean_norm_g(r['sucursal']):
                                        row_found = idx_row+1
                                        break
                                except:
                                    continue
                            if row_found:
                                if col_rep_idx: ws_main.update_cell(row_found, col_rep_idx, r['no_reporte'])
                                if col_fec_idx: ws_main.update_cell(row_found, col_fec_idx, r['fecha_reporte'])
                                if col_falla_idx: ws_main.update_cell(row_found, col_falla_idx, r['obs'])
                            else:
                                new_row = [""] * len(headers)
                                if col_est_idx: new_row[col_est_idx-1] = r['estado']
                                if col_suc_idx: new_row[col_suc_idx-1] = r['sucursal']
                                if col_tel_idx: new_row[col_tel_idx-1] = r['tel']
                                if col_rep_idx: new_row[col_rep_idx-1] = r['no_reporte']
                                if col_fec_idx: new_row[col_fec_idx-1] = r['fecha_reporte']
                                if col_falla_idx: new_row[col_falla_idx-1] = r['obs']
                                ws_main.append_row(new_row)
                                all_vals.append(new_row)
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        log_acceso(st.session_state['current_user'], f"Guardo lote PRUEBA {guardados} reportes - Reemplazo Hoja1 + Append Historial")
                        st.success(f"✅ {guardados} reportes guardados: Hoja1 REEMPLAZADA y HISTORIAL agregado - Cerrando sesion...")
                        st.session_state['batch_reportes'] = []
                        st.cache_data.clear()
                        st.balloons()
                        time.sleep(2)
                        st.session_state['admin_auth'] = False
                        st.session_state['show_add_form'] = False
                        st.session_state['show_login'] = False
                        st.session_state['current_user'] = None
                        st.rerun()
                    else:
                        for r in st.session_state['batch_reportes']:
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        st.success(f"✅ DEMO: {guardados} reportes guardados en memoria")
                        st.balloons()
                        time.sleep(1)
                        st.session_state['batch_reportes'] = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

# --- DETALLE CON FORMATO MEJORADO DE REPORTE Y FECHA + DIAS TRANSCURRIDOS ---
if not st.session_state.get('show_add_form', False):
    if 'estado_real' in st.session_state and 'sucursal_real' in st.session_state and COL_EST and COL_SUC:
        estado_sel = st.session_state['estado_real']
        suc_sel = st.session_state['sucursal_real']
        if estado_sel in df[COL_EST].values:
            df_filtro = df[(df[COL_EST] == estado_sel) & (df[COL_SUC] == suc_sel)]
            if not df_filtro.empty:
                for _, row in df_filtro.iterrows():
                    rep = str(row.get(COL_REP, "")).strip() if COL_REP else ""
                    fec = str(row.get(COL_FEC, "")).strip() if COL_FEC else ""
                    obs = str(row.get(COL_OBS, "")).strip() if COL_OBS else ""
                    tel_raw = row.get(COL_TEL, "") if COL_TEL else ""
                    tels = split_tels(tel_raw)
                    dias, txt_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")
                    
                    # Badge con dias transcurridos - formato mejorado
                    if not tiene_reporte(rep):
                        badge_html = '<span class="badge badge-ok">Sin reporte</span>'
                    else:
                        if dias is None:
                            badge_html = f'<span class="badge badge-warn">{txt_dias}</span>'
                        elif dias <= 2:
                            badge_html = f'<span class="badge badge-warn">{dias} dias</span>'
                        elif dias <= 5:
                            badge_html = f'<span class="badge badge-orange">{dias} dias</span>'
                        else:
                            badge_html = f'<span class="badge badge-red">{txt_dias}</span>'
                    
                    # Formateo reporte y fecha con iconos y cajas
                    rep_display = f'<span class="rep-box">🗂️ REP: {rep}</span>' if tiene_reporte(rep) else '<span class="rep-box" style="background:#f0fdf4; color:#166534;">✅ Sin REP</span>'
                    fecha_display = f'<span class="rep-box">📅 Fecha: {fec}</span>' if fec and fec.lower() not in ['nan','none',''] else '<span class="rep-box">📅 Fecha: N/A</span>'
                    estado_display = f'<span class="rep-box" style="background:#0f172a; color:white; border-color:#0f172a;">📍 {estado_sel}</span>'

                    # Color del borde del box segun reporte activo
                    if tiene_reporte(rep):
                        border_color = "#ef4444"  # Rojo si hay reporte activo
                        border_bg = "rgba(254,242,242,0.5)"
                    else:
                        border_color = "#16a34a"  # Verde si no hay reporte
                        border_bg = "rgba(240,253,244,0.5)"

                    # Tarjeta principal con formato de captura y borde dinamico - CON BOTON CERRAR REPORTE ARRIBA
                    # Si hay reporte activo, agregamos boton en el espacio vacio de la derecha
                    if tiene_reporte(rep):
                        # Con reporte activo: layout con falla a la izquierda y boton cerrar a la derecha
                        st.markdown(f"""
                        <div class="glass" style="padding:20px; border-left:5px solid {border_color}; background: {border_bg} !important;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px;">
                                <div style="display:flex; gap:14px; align-items:flex-start;">
                                    <div style="width:42px; height:42px; background:#0f172a; color:white; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;">🏢</div>
                                    <div>
                                        <div style="font-size:1.2rem; font-weight:900; color:#0f172a; letter-spacing:-0.5px;">{suc_sel}</div>
                                        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
                                            {estado_display}
                                            {rep_display}
                                            {fecha_display}
                                        </div>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    {badge_html}
                                </div>
                            </div>
                            <div style="margin-top:14px; display:flex; gap:12px; align-items:stretch;">
                                <div style="flex:2; padding:12px 14px; background:#f8fafc; border:1px solid #f1f5f9; border-radius:10px;">
                                    <div style="font-size:0.70rem; font-weight:800; color:#64748b; letter-spacing:0.6px; margin-bottom:4px;">📝 FALLA REPORTADA</div>
                                    <div style="color:#1e293b; font-size:0.92rem;">{obs if obs and obs.lower()!='nan' else 'Sin observaciones'}</div>
                                </div>
                                <div style="flex:1; min-width:200px;">
                                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:10px; padding:10px 12px; height:100%; display:flex; flex-direction:column; justify-content:center;">
                                        <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
                                            <div style="width:22px; height:22px; background:#ef4444; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px;">⚠️</div>
                                            <div style="font-weight:800; font-size:0.75rem; color:#b91c1c;">REPORTE ACTIVO</div>
                                        </div>
                                        <div style="font-size:0.65rem; color:#7f1d1d; line-height:1.2;">REP: {rep} | {txt_dias}</div>
                                        <div style="font-size:0.60rem; color:#991b1b; margin-top:4px;">Acción requerida para cierre</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        # Boton CERRAR REPORTE justo debajo del recuadro, alineado a la derecha donde marcaste
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        c_btn1, c_btn2 = st.columns([2.2, 0.8])
                        with c_btn1:
                            st.markdown("<div style='font-size:0.70rem; color:#64748b; padding-top:8px;'>💡 Al cerrar se limpiará en BDSUCURSALES2: No. REPORTE, FECHA, FALLA → vacías. Se guardará log en HISTORIAL_REPORTES.</div>", unsafe_allow_html=True)
                        with c_btn2:
                            if st.button(f"✅ CERRAR REPORTE", key=f"btn_cerrar_{estado_sel}_{suc_sel}_{rep}", type="primary", use_container_width=True):
                                st.session_state['delete_target'] = {"estado": estado_sel, "sucursal": suc_sel, "rep": rep, "fec": fec, "obs": obs, "tel": tel_raw}
                                if not st.session_state.get('admin_auth'):
                                    st.session_state['show_delete_login'] = True
                                    st.session_state['show_delete_confirm'] = False
                                else:
                                    st.session_state['show_delete_confirm'] = True
                                    st.session_state['show_delete_login'] = False
                                st.rerun()
                    else:
                        # Sin reporte activo: layout normal sin boton
                        st.markdown(f"""
                        <div class="glass" style="padding:20px; border-left:5px solid {border_color}; background: {border_bg} !important;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px;">
                                <div style="display:flex; gap:14px; align-items:flex-start;">
                                    <div style="width:42px; height:42px; background:#0f172a; color:white; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;">🏢</div>
                                    <div>
                                        <div style="font-size:1.2rem; font-weight:900; color:#0f172a; letter-spacing:-0.5px;">{suc_sel}</div>
                                        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
                                            {estado_display}
                                            {rep_display}
                                            {fecha_display}
                                        </div>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    {badge_html}
                                </div>
                            </div>
                            <div style="margin-top:14px; padding:12px 14px; background:#f8fafc; border:1px solid #f1f5f9; border-radius:10px;">
                                <div style="font-size:0.70rem; font-weight:800; color:#64748b; letter-spacing:0.6px; margin-bottom:4px;">📝 FALLA REPORTADA</div>
                                <div style="color:#1e293b; font-size:0.92rem;">{obs if obs and obs.lower()!='nan' else 'Sin observaciones'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Lineas telefonicas con icono
                    st.markdown(f"<div style='margin-top:14px; margin-bottom:8px; font-weight:800; font-size:0.85rem;'>☎️ LINEAS TELEFONICAS • {len(tels)} numeros</div>", unsafe_allow_html=True)
                    if tels:
                        cols = st.columns(2)
                        for i, t in enumerate(tels):
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:10px 14px; display:flex; align-items:center; gap:10px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                                    <div style="width:34px; height:34px; background:#eff6ff; border-radius:9px; display:flex; align-items:center; justify-content:center;">📞</div>
                                    <div>
                                        <div style="font-size:0.65rem; color:#64748b; font-weight:700;">LINEA TELEFONICA</div>
                                        <div style="font-weight:800; font-size:0.95rem; letter-spacing:0.3px;">{t}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(f"Sin lineas registradas - {tel_raw}")

            else:
                st.info("Selecciona sucursal para ver detalle")

# --- MODAL LOGIN CERRAR REPORTE ---
if st.session_state.get('show_delete_login') and not st.session_state.get('admin_auth'):
    st.markdown('<div class="glass" style="border:2px solid #dc2626; padding:24px; margin-top:16px; background:rgba(254,242,242,0.95) !important;">', unsafe_allow_html=True)
    st.markdown("### 🔒 Login para CERRAR REPORTE")
    target = st.session_state.get('delete_target', {})
    st.markdown(f"""
    <div style="background:#fef2f2; border:1px solid #fecaca; border-left:5px solid #dc2626; padding:12px 16px; border-radius:8px; margin:10px 0;">
        <b style="color:#991b1b;">⚠️ ADVERTENCIA: Vas a CERRAR un reporte activo</b><br>
        <b>Sucursal:</b> {target.get('sucursal','')} - {target.get('estado','')}<br>
        <b>No. REPORTE:</b> {target.get('rep','')}<br>
        <b>Fecha reporte:</b> {target.get('fec','')}<br>
        <b>Falla:</b> {target.get('obs','Sin observaciones')[:200]}<br><br>
        <span style="font-size:0.85rem; color:#7f1d1d;">Se requiere autenticación de administrador para cerrar este reporte.</span>
    </div>
    """, unsafe_allow_html=True)
    u_del = st.text_input("Usuario Administrador", key="delete_login_user", placeholder="Ingresa tu usuario")
    p_del = st.text_input("Contraseña", type="password", key="delete_login_pwd", placeholder="Ingresa tu contraseña")
    cd1, cd2 = st.columns(2)
    with cd1:
        if st.button("❌ Cancelar", key="cancel_delete_login", use_container_width=True):
            st.session_state['show_delete_login'] = False
            st.session_state['delete_target'] = None
            st.rerun()
    with cd2:
        if st.button("🔐 Ingresar y Continuar", key="confirm_delete_login", type="primary", use_container_width=True):
            if check_login(u_del, p_del):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = u_del
                st.session_state['show_delete_login'] = False
                st.session_state['show_delete_confirm'] = True
                log_acceso(u_del, f"Login para CERRAR REPORTE {target.get('rep','')} {target.get('sucursal','')}")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MODAL CONFIRMAR CIERRE DE REPORTE ---
if st.session_state.get('show_delete_confirm'):
    target = st.session_state.get('delete_target', {})
    if target:
        st.markdown('<div class="glass" style="border:2px solid #ef4444; background:rgba(254,242,242,0.8) !important; padding:24px; margin-top:16px;">', unsafe_allow_html=True)
        st.markdown(f"### ✅ Confirmar Cierre de Reporte")
        st.markdown(f"""
        <div style="background:white; border:1px solid #fecaca; border-left:5px solid #ef4444; padding:16px; border-radius:10px; margin:12px 0;">
            <b>Estado:</b> {target.get('estado')}<br>
            <b>Sucursal:</b> {target.get('sucursal')}<br>
            <b>No. REPORTE:</b> {target.get('rep')}<br>
            <b>Fecha Reporte:</b> {target.get('fec')}<br>
            <b>Falla:</b> {target.get('obs','Sin observaciones')[:250]}<br><br>
            <div style="background:#fef2f2; border:1px solid #fecaca; padding:12px; border-radius:8px;">
                <b style="color:#b91c1c; font-size:0.90rem;">⚠️ ADVERTENCIA - ACCIÓN IRREVERSIBLE EN BDSUCURSALES2</b><br>
                <div style="font-size:0.85rem; color:#7f1d1d; margin-top:6px;">
                Esta acción <b>CERRARÁ el reporte</b> y hará lo siguiente:<br><br>
                <b>En Google Sheets - Hoja BDSUCURSALES2:</b><br>
                • Buscará ESTADO = {target.get('estado')} y SUCURSAL = {target.get('sucursal')}<br>
                • Limpiará las casillas:<br>
                &nbsp;&nbsp;→ <b>NO. REPORTE</b> = vacía<br>
                &nbsp;&nbsp;→ <b>FECHA DE REPORTE</b> = vacía<br>
                &nbsp;&nbsp;→ <b>FALLA</b> = vacía<br><br>
                <b>En Google Sheets - Hoja HISTORIAL_REPORTES:</b><br>
                • <b>MANTENDRÁ</b> todos los eventos históricos<br>
                • Agregará un nuevo registro de cierre: <b>CERRADO-{target.get('rep')}</b><br>
                • Con log de usuario, fecha y hora del cierre
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("❌ No, Cancelar", key="cancel_delete_final", use_container_width=True):
                st.session_state['show_delete_confirm'] = False
                st.session_state['delete_target'] = None
                st.session_state['show_delete_login'] = False
                st.rerun()
        with cc2:
            if st.button("✅ Sí, CERRAR REPORTE", key="confirm_delete_final", type="primary", use_container_width=True):
                try:
                    with st.spinner("Cerrando reporte en BDSUCURSALES2..."):
                        ok, msg = eliminar_reporte_hoja1(target['estado'], target['sucursal'], target['rep'])
                        if ok:
                            # Log en historial como cierre
                            log_eliminacion_historial(st.session_state.get('current_user','sistema'), target['estado'], target['sucursal'], target['rep'], target['fec'], target['obs'])
                            log_acceso(st.session_state.get('current_user','sistema'), f"CERRO REPORTE {target['rep']} {target['sucursal']} - {target['estado']} | Limpiado BDSUCURSALES2")
                            st.success(f"✅ Reporte {target['rep']} CERRADO correctamente. Campos limpiados en BDSUCURSALES2. Historial mantenido en HISTORIAL_REPORTES.")
                            st.balloons()
                            time.sleep(2)
                            st.session_state['show_delete_confirm'] = False
                            st.session_state['delete_target'] = None
                            st.session_state['show_delete_login'] = False
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error al cerrar: {msg}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)
