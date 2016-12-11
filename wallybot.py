#!/usr/bin/env pypy
# get shipping address
# https://www.walmart.com/api/checkout-customer/:CID/shipping-address
# get card info
# https://www.walmart.com/api/checkout-customer/:CID/credit-card
import requests
import json
import sys
import time
import logging
import argparse
from apscheduler.schedulers.background import BackgroundScheduler
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
bot_detection_string = "MzI1ODM0NjI0AAAAAAAAAB2\/fHSNf724MiOJ1nzU03A1SWU8SRVHFUY1lPOwKeCjvpCv9t+PjeXwy2gjTjEYVdwYE\/T9SDxDTo4qOz49rB0y3iE\/OHjyMkKyZTPjfNqAQaz1V695J1qyp0GpRJ8TGNUGBc5PpjKX8lwuXiyFPenpZTcP524HoxVaLJWouS7p0FyGpy3RmHQENiWPUUQmSAHfUy0L+Dj6\/fwhWJszsZuL1zv7O5vLsAMg6xPi59cgLlLlqfpf7vBqfD1t86Acj5Xt+trkJwzUpTdsM\/vRGfJkn4wc41Syc0\/HV\/NcZku0U9MfiQeDUeL5GLD0j0eLmKDYD8lIZxZrKbw\/hp03eRZSFoq7OuLc9dQCDS7i+4\/EicwXYZIwTfonIbUFCsrPffYyDPgKrJSvz6ENm5Vblb9nC2HodmOJStm10u6zRVYY4pWE+7ZZ4XGZzERw+cjo3bofVdJsvneYvnH82dTh+C7h4FUpgMdI1Bb1Jz46aupnkSSEmo9Q+CEYBmCQzf97pOWwpKdIyolccwLnunSFARzVG09Hxm7c+Y8KxusoE4eDlEZ4GcnqNW6wWue1XUhcRrEh7x1uU5pEQwxabesZ9QnOkFaiDbM1fIdhulk7oPJ2KnLvvtsJvRDKnXN0cuhWeVmMPSlBfuXCOiTnqgZSNLpH1e77nh3f0A3+w6A9j6odeAAGzfZ0+wv4Ly+38ei2YK8\/HuFTdTtdjXW\/b6LXRvV7lDDRNjJYgwf5xVwnruN4Mun\/o9xrVuGTzh3IcdTj75RnzIS288k5qzExY+3Y0mVfX00lJRVl8Tg3s\/uIYdYTocF7XxFw+dLjqQINafNAyhSR0MBtqc4wqOlUQKtkPZCgOgr\/w7pWACcjtAZveOVSoJeKqz6NMvf+FgQT52cWf+sDuJ1XwsSGwzXyipxIR+2W0EXw3nhLWPmh\/ufhfaYrgjHwu+INEXhzmldG0cK34dg5ny+NPZvcUAHYnXXt7SP3LhBSRtG6QAtqjU1ffxxQLrxN9pb82odhdGA775G2mJaNxzgAjd16+IuDQv9oat7mqMwyzaVSNX8A3K+Mg05zvqVcOBCpUfA1eb817Syc1\/fIAhNbcCrhqoNQ+Ye4aEv0ZRY3GHBngut+0N6eVaSErRnLF2utxRYNmFF4HuPoiMjOVOWqI57IsFLCEjsNNkaU+Y33mdus9w0iQOzra0BdrMCWEsESCcBJyVBF2pee7npSpuEv8uh4DXXUUggShbdb7y\/jPfu85DfL8DJRDFSWRppHPYUCpN4kEhUfrykVHfxVN41+lvPVoSgT\/50y\/ONTu3EEJe74veJiZoaNE5IbQ2a5C6Cbz2eOzA0KZy9JucePbzwwL\/q9ivP\/0IGD9NSWtWXm3Oefflpa5MF9euVWSlYMOYV5bDONZ5ac7\/vO9M5RF6xdDFsT2QkNB\/qMn2IChip+xGmLBHck7gd5E9QkSkyu\/DdZhwnL4Dg7eddiOwWvoqCiZj4AwpuaRRX6zxU0dXrwv7uSSqN8PaLOBW2IPcz3ULU6HgFkeGyTGz202SalkQcihoHHsHMCYlc\/8rnjTzReaZgTCfQuvFYKB3NGOMKCKpwvlRxLw\/AuZQLiYAYq9ZMGihw+VRrx0VAXkG9RltQ6mDLegGNfm7E7aeLXMkHP6VszxeNKH1TA1dQcYgS6pxn7I9W0QmpY437HjALacoUUUmpMjqULFtWJIDEwYoYXRQOrBnZB5v90hCDRq5Iwo0d51ZohJGnJtHlQiNWwMvwPa7hnejgSdRmRq\/lVFCpx6Tj4sl\/fAeDWF14kUkvxKxnZxGVF9aR3mRVUfpUVLRpWbB3qIRoxm5chG8QdR9ldmlA69wSm2S9mOTB6OS1\/AaIt11C5qEpmkQ7XiIqiRLqFES0yt+urvVO5M46t6qJGSkBqTufh9qZpxMwZNywB6+68l4H0TcEyBBs+wuoQ2r8GXMxc4Bjha3kB8CtXmrOMBroDZawbPchOmCNMAOdAlSDmzFjvmZZkut3jHLOnuzNvUHjvMm7XxA7EsSBE1Rh1gew6VcAJlCMx5SZaES6RBR0VwaFLL5uu7cJV6DaeNBE+dcY2M8U9Lv\/DpWSRJGWJcymo38Tw1\/RaMtsiruP7czuyaFf8Hfo6oadJBtZLyFOgTK7zGiRMsnLVVmau\/2+RJwiN8W08VYwsJ1SURf7PWOnlq3DFaBGT9yv7uZMB73CH9mHPWKfgnJa5BZ6amh76X+\/IgSzF8ENCDWtIJYPK7kTOlC83ZbbZFveaIlt2q8Oac4zraLiq8ar5TOd2iiJygtJcgYrQ0M9h8lsz5PDu6bgmGxw7C0rpBENMMocKVfi5MTNS5X919XQLHHR2EtkVv9FQB1fAEOnajLIpDQ\/ywAU+DIPwPRSfZMRQ1G6F4oJjkcGOkZ9p4jDJ7Jm7zFlRxGCYLOpc3lfGHxdDK6ljyFSadozYPaRRST2NV4rtc9S4M20Ar4VkE2iSETXTsO17nF\/b\/n3Kk7agTEmHAz+dRfqCZPYeyrIxc\/21z4bumEL6aBI\/puPHh0fpsXCW3SHWnR708Mu6JbE7bsL5XTAXM7fG\/cua6HybDTKKNJWF5br8+7fogn3oZsttwRC839BQvnp3qNoU0VFPXeV6FqsNVXTp4fC4AEMO3xKpHAi30a9Hq65End04uZC1HMpIcqeFjVVdYt+HySIf0nydeKqwPSSFv3PEboF5aQl2LPSw0oVIcV+BfV1xiCP7qR0KM43cPssWEDcAFrsw9DfYwd1z7n7J3FI7qhw8GOxVs3h2xUYbSE0JAAH8LNRn+HKbohj77\/\/UcQDlorTGgvmoVc4Fj4czAUm9ZAU47\/mRMBZO65mkuqb\/gMgJhzzJlcc2ZdWEIqVb8QE1KrPvsILUz5Qrz\/qOcZIzjgC7SKXADVGpxyvCWl3gLw3mAzmUJhpxxLMCxu05Q3q97CMOITF\/k3wvrJ4VJT91UDDI8qT+\/lj\/cW8I1pFRR1ci1YbhUG4ZAxJBol4b+7nJSs0zsm4DfhfcTG6JfF+I9JYQkvI25yaBWho9lnSI\/5VN\/Kyfr6a2xrC6CVZD+iY87W5h8g0ebcaClhhzAByjbrMY3KtNmEKPsaaDyhImOmALGKU0u3jMOHayC\/xGbtSx4ZVw7Y00GFrNp3x409\/tvadYMHNYtUSQ5ilf5SRGUQ2wgndGLYzKxQG\/UtjIrtyCnde99R3Sbh0xle4naJdgeTOorX+++rDyc+QJxGw4Zz0XLEOCvkFUb\/YL3oZpGZ9vjbJI49gtoLjtGWHBVEeIgN8jTpIIX+kAgCaFA1KuqTR85xg0i7OdFuZ4Kc9i6czhLc+PbvqglAkBL8x3yYycM7O45HPjQr2T6nfHcYgTdcUrYpA9VJyCnNnLI9xFgJ0iDb1FTJI01VJhNHhFw7oKLeK0KksrS0Oh21MIeoBURXcD0FCuFTMIfv6EGF3y\/6tNuLs+QleXZIZf2Z8QpBnbIX2O6P6PiQMbio3UwGm1DuCSyIA12VeVGkL1cm+glQ1EaLrOGDQbG6cL\/G4e4eFSN6nKTYDGtGzPakZOK+epCIoocK+khyIXmOkxOKgVXBv0QOFdE6WXOD7MC3WqqYL7fbM5ztR8IQ0FTt5X7Od9e13UNxYXqxu5tsRpZF8nQbDvplEFBrTLOjLfWSCn7V7ZbnjYN7V1w97Y2fNzURoCc1tax8bn\/1KSrtvIp\/rC1vpLnLfyXPGY0iqW4ON4iLqoe3jU1e8rBEEalH0ZyW1j\/oz1lyyCi8b6dvOnjLoTTx7v0AU7ORTc7Zf+IWEnv2mfjuINKW2XFbBu6rF3xS9G5tq4TjgALNeFwOznSrmF1JYSCrTbHyvNCgfYj\/877UeYDRDMsto\/8rU7hOf2gISIIZ+sBRpHXq3ibrb+BM7MnBeF8pT6EZ9aYl2iU+JJETa39Rs\/B+3B+3oVEg5OBtv\/hCTafnCLVgY7omWoAshFhzNvU5trPlt4e808fWsUbrU18ufu69XLON9+KZ2GTTljNpcOZ66LyZ61tWHX4JKvSLVY+GNhvF9ywooShCJvMjdA6F7ztm086pANIQwNESg7Ifcn+IDOyX7advdQsiypzRlp1fUIQz0ELDioFYYmzwnpg1j3T0\/XL\/\/gliwnz0WwYhmOxHttHwq2HUUajsrHa67DWea3aW6LFBNkMbOkMIzHYmVu\/BU4dJJt1gzv6bSNKjkCsHeY\/lzRwZEybrcyAv8alZnfVqJhSvHulkOnY98u9ve3UxmNbSmtgWCSvOvjH4hoPW0pMO+kUMgTT+bnk51ok4wdwXUzDlnI6jlla6Zq6feopkldplZlu3AEbVXl\/PxkjTt\/y8kNPzo4g25XmMb+lZBXWXEmXlIfnyTQKg\/RyhQWSiIf\/n9EQx2KcJ81Kb94Yv3XtVLFVhWEXfDXDCTwKvVopnYuhuOffMuuhsTWoeAkZWX4dRT58ljn+uHf8uAMcILHqJIwVD44tFpRwVyMCXQfTeVMz\/3memCNBd6am6KrYvbv42gJwlFWMobffX09wO84bFKs8IoTRXz3Z8+o9zrEZhY1Nkuyc9pKb9lPHKeHbPHWNeT0vLY18aPD3uS2XEP4aSBDaDeNgGW\/0Kw9KuWceJUcCht\/0KaNAhSeT98u67Dl1l6GxdhhmB9Umm0ks9rAzFL4QJML4sImgpNS7yqvcTnrf+sx\/7UxavAsBFXUbkqb\/j+tVeRY4SrweZSH7QmlCXbQS4dnSY2slULwX2i0c3YAr48WKGsZhAQMX68KXFZfRbWJiqpap7CVoIMALkciZYGBHnIhqZ5+k4S5S1XbyyBP0Pf528Jja0ZaUDzhL0USdKYl6AzT9H2aX+bJpA5J4vYPD\/e4Hf6KVSkz6i\/sjJWv8ZpkvVr0CjJr11MJTAQ5Hy7B3onjcAH2xQqBCVgdJwFIdmt2aaJ79u5DEFlBezRg60qseXrqZI42yHWy6JZ92yvqIYtz4M895gAAM+kZXlpfMQl4\/wuyJN4\/5Ow5SKb+xNDF2IKYpdECyeTkUSiEeu9UWMgQlLVVqQNyqm+N4hF4HmfH8zC\/Aa\/pVnD7R3j7C6505TpaI5EmpYByCBchQZg8HYlNvMbptXPBjCZYRsWUx6Dfa4OHSnZz8qkqi0b8+TqnEC5udHjCjBg3Sadf7QVE2kYjVNQLsdFtm6g0QBuJqH5tHWb5jBurswGJzqbqWqxO80kiOp\/R4lhSJ5lN7+j3v2DVBF1PYzvOr0cDCDZthqed0sfTtBvT8X7oqw1N3q5VqlonCgeUL02F6Ds2QbynMvUOed9aZEfvIKVMw1Yn46R4LiVYETfo55Vbul5hEScIWTOxnmkC41gd7rS2z6Fc3yAr0JfnSvKXFk1uGAsyczltOjUlLaU5QImQDBi0ibL2efcKQUj6EzCmfEBLgzkaEZZs+LoRGKyG9CCrfMw6utXCtx2X3Bqu0xim3hdNdj\/n6uaMkXEgC1AyUwSaIZx8493uqU1wOAyKIad7USXMegA81vCGTTpKEup557CyP\/lG7b2BV8YlImlVMQwqXF2m9LnBkgtCmiLZTDe2zg2eGOVm9apvcHhXg5TosWpec6sr9ZtPX\/Q3PAEvrGw\/yF5g\/7fstwHZFm8aOHNc+KZsCCqKGULVBNvOGnrsk4EKnorNIGQfAdANfB00JTRtlENUJTSG6O5QvWnws5TShJoj6NXN8DSpuITUxVMgVEvMf1sgkbmNOs81aF1lBaMM7T\/msJA65rkSOayJrkqoOICa+KSIfcy8FZSyVw1gKyavU+YAPR7SJW++lwE2emfyB7tzp3gZJZDxsXyjTOXp244UWrdv6xzPB3nS3r\/sh0tpGr7dC0TsRDbu5tu\/5MOCdAxPDo80rFKCoBtuUJi1p2x5zWu8Hz7+UJZaC4zyy2Ezo9N5Umvg+NN9mJndZmzZsTMoUe5+E3NQt4hi4mww2bXJwfeVi4qrLbRbjLtIsnmjwYlcFA3hh2V+RRMrgP\/ySkxHiIXddJyBFBlS9djK2zAGsG0Oa5mxmnuoavSqARnW+Psv07z7s\/ATkCEzhj\/r\/gtJn1+OBkX5lR7girCDpivn6J\/ijnNrISnLd4c10Aqoi83NiAybN4pLkFK+xF3NG2SPyQzyq1BESZFkDkkNwHEbUjHuCT+3879IRCkj6Qe2rK2BXtPL1OAy7zAPK6\/tVUdcPJ0BNeHjdPm90E9n7WftsiFUGkTUwCnEjci9\/4jLi86u5BE78uPsyOSLB4Z6qrpI5yP9OD2ToV6deGFe76iJ3gnsM18HAA4e3Yi3Y26GAy2I4hbFNT\/1zu96VYEEId0TC5TlE6yh4t31Oq5jC+oaAwrg66CpFN6b7XucRCIfX2Pbm5segCJtQ2jebeNE1zXu7ZEQgkfWI0fG4rAR9MDJWB58pFloJjfkgFscsrJ0kdNReijzoAazQnJSb8ffr31I39Z96a4rIApfZb+zXB83VDZKlXCdmLMQ+eM6hEkYrRNMi9HuvF0EG6eenECqviWnlp7v5\/83lQzwpmfxra+FSGDt9ojnBtqKRjzA9Rkt8d4GM1OFn2jBkQfk\/NiMQ1gcDB\/R8zUGMDmoUeNyx911smE6rY9MJyBuGxqkzWtuqoQVldjYLHJJr0yiVZrUAufT5r5S\/T8J\/KvzGrHlURT25SmPKcfoU9NuiJGC+af\/617jLWKq0U5TKxIwGAlC+uGrIB6mqGaQtDwftEpfL8AnnDLdvRbvm1Uj9fycU\/aecIL7ipi3D3DEC71Bv16+uu79JCROhZRxNYTEiIs2n0bHfg8wQug5oYuuCotMIL576lrqFxGsI0d1k8JhI3cDe7Mn5m+Y4ROh+BKQIOHexA0FvI9n6s9vI5eNKuDDD+7K+2GC2Ar6Ym\/OgDSp8At+vZyzbDA7ECzDn9dmAzS\/+zXcnBQuh42ou5QWssORnngo+tTOOoWr28pUbsX6IiUTY89lkO1pWCy9sHmbHDlz9Gfnbmwvoa3UDbb8OGD90X3B9elwud5BVeEwXMQqts7yQ5LOtwOb2P1dkHznSqY4jsJbjt25JP3lONjFErKBXX7izEOW7PypVbNlKKG1NGV5qo78Xll5NeJ18sx9n5Q7TFNDZ2N1azgA20d0pz28ZmMn3+na+mJUxlq96wehiONbRIapTePLCNUbqgMUon9pChx6XbZQsTNetbdw6aZsK6bauSQXN2QFL29DYePtzgtedvMTs+4AqDUg0RA+Drvlp29sdtSLTLLw9PnZYDXxzHM6Af7LVc6pVPUAeX5hqMqmY4yk8Tw2aC\/tQmFhu49P8Tkh49SvXYzLrIy5YxtBVpVNSCOQ0CDLoMQmnbn\/nzdqS+v\/icNNw0GSS1NRApMO8v4uiL4U95L1wysMsKag8ov9xriI3clvyYeEzJFV5aXGC+AzzENQIBWxleHZLNsrjbxgR9XUxf+x3KbJP5lD+GxXXgMuiNEtkb667HKtaFlXLH2wFRFRYEZHmK8nyBSvl\/bbqQ7G3G8VObX5CK99EkMJfPqk10LCtPbvDPfLOsXuYRd4+ut7PMT+o3iW2+PAkppAGG1HGX90ekOu8avzXnqB90d9\/gdssAP9X7Ux2838wFGT9Ils9X4hgK15QkXxI04DcZQ1UKnd2gvEHR4GNVWX97n1uGJjQIxp2irytfq4QujRPxyFlhCn6HEqB4NJq2MnFT7zG0JaClaQuOFb1eb5ZUQ8\/NTZznFe0I0cibjj5FqYBVfJNFXQav2CO+\/6lmmJ91i3qqWDyuTtctommjLaYlzbxdQ4xT7Xr9OqquIUlmah2y9cHgrKB5dzKQm14t6+I1dBEDSUKclhssuIRXz5XMQDoSQfie1lbIrYDPMWUoQ9VW3ee3GgE4U2e5cip9x1530jGUQw\/VQ2zr0rt1yGpJlzY\/7dNbhupZVhWewSxIIMTcEIIp0RMNaHWumX4yQpE\/AUWZMfsHOb3h2fuac3y\/6ldDwhGWTDkp6+gLdDb48JTKqNf+VB0RtmQ03FQLPILJym2wNiUqOJs\/2ebepV4VC0wGgLP7ZB9Vh1T7EufXSi84prHrqitcRa\/IfohitkeYpruCtGLjCwzeRkFI0UET785heh0pnEwIsxVf6SpLtRmOStMprbzcyirc+za7coxUWqOpJR60AvpabbRz3Te2fUeYOFZPqGmhFbM7EXy+8raQEKtfOL4EDOe3UJEDVWmnD9ISixVu8HOxDKMqdndXBekJAIyLJ61OOFkX07eGDv\/JKyKslrYBGgnwWi3K2EBVgTomOb7cSMxsNY7+NX3vWKNYdYA5qPrwGnbBPX9kfc8MdzBlPRUnGfxJaCOMC1WtX1nIBX7aJ6YaHwJRBDiM4UEEu9zbv+FlWj5zghEcs7sdh\/sYPNzGlKWzMYNrAV+VngQhfLXfAcvd+9gA+SavafvdbK4otS8LNFRhWN46m8szb4VnwqD6ZiZFbZM8A53Gwy+ieT1VaQfjk7GO\/di\/l6V4nRw\/f\/EQHaAF7LBYJHZXwOnPyhvxsnRcsy0Aq3uOw8fmuUOM8+Ic8ZBfkbjLucVD3VTt3iNCnjCxYAt+uKicSUYEWwtqfDCMNb1L2r9YdfELS3Y8wanD5I8AhmPTFyRT1KpVuhN3DXKBVxoIjeYBqIRPUtXGlWkPu9FxxgUKKOZm9TjPUuNjuB\/4bXJ75bFFLjRXmkmnW6dvtNP6ENe2PqYc0NeQsLcFWF3Sx8RKkYnhpRYlXF7ZYNvJ0yJaQwyMawnv7AlUYPiLve4gwFS6kHHCGf1BffXkzR1AG5rNvCZaEL+BbT5GOxgGwBZga4\/dvd\/2IZVG3AG3r5eTJIuK3zEAUAoGXvMscNsSroww2ulR7EzCLuWJ2CayxRNMPcQ6ZR9BjMuA1as\/DoUk955cXVShx\/bK\/yHyckvVkZ41rjZK+X2hG0uOrlJSm7sYexrLxgE\/svJChUH6oq6ayHedqvSa1W6zgvzr45Jyt0GfOOgcsmj0wNMDZGtFT\/HYBf22vpoe97t4EFT4J9MT8avCQQTCXwa2KgmncKnDmxTpYpA0qdxaQVB8ND1ElxLLP2qvzJ\/FCE0rsNEeZFoOdahY+3QbsvV3GPx7ejSN+h6Lbllw8BrGNHheq0SQGctu1tEz6j4\/a6YXEaZ4WAq2OrnfJFNdodTcBw4RPUVYUMLybub2C0wW\/mgWp1IYwcE2gBdfszTjfas5y4+GQ0l3y04UXemIqqrhd9LOa5a46lFnInYd6wwoL6oHroDpVi\/3VcbUz5fqUsAS1cpjlJBeD7bxkty0Z1keL5uyZGj5rxSvFEwQ1oWRqNV7C\/S6eXz4aYksc6+dg1x87\/52Qw+RQUChlRPaIff88D9DikkqjI1YRt8567ZweG9LvQwL71n9DFY2bJyasE7VQdcyPBycPqzLIrWg7fSB3qzqERs7c84\/9+blVxIP95iNSjFWGHYEZURw2tW9P6wRKV3mH0eXHMmMhxFgdFRAURPEGXKlZ7aXd1QJV+BsKwTWB6PDBMtAeGN7ixyStrKmuiWM6YJZQYvXpBfjmkBS6M2crncHTceH8Tucz3QTyfkIUZB1JSfYhs18tbeh032T2FiLCnn+9hFTzQatdQRq8d9LQNFIkFwiDvl26nwJheBm+DVzKwFONadEx4JsS0IZ9hv\/fkXS\/V+tLUbmbRoT5z1kPYLLw7Ap9O1W1wB\/34HzWWJiNlkp8drFyszXLjiTn19hmT6empMMEcE91YMxT8bS9D8oET+097+0106"

def walmart_pre_signin(r):
    logger.debug('Running pre-sign in tasks.')
    r.get('https://quimby.mobile.walmart.com/m/j?service=AppVersion&method=getVersionRequired&p1=com.walmart.electronics')
    r.get('https://api.mobile.walmart.com/mauth/v2/shippingPassEligible')
    return

def walmart_get_offerid(r, productid):
    logger.debug('Running walmart_get_offerid({0})'.format(productid))

    while True:
        resp = \
                json.loads(r.get('http://www.walmart.com/product/mobile/api/{0}?location=01906'.format(productid)).text)
        logger.debug('Walmart get_offerid response: {0}'.format(
          json.dumps(resp,indent=4,sort_keys=True)))

        try:
            _offerid = filter(lambda p: p['seller']['name'] == 'Walmart.com',
                    resp['product']['buyingOptions']['marketplaceOptions'])
            offerid = _offerid[0]['offerId']
            logger.info('OfferId discovered: {0}'.format(offerid))
            return offerid
        except Exception as e:
            logger.info('No WalMart offerid discovered, continuing...')
            time.sleep(0.2)
            continue



def walmart_signin(r, username, password):
    logger.debug('Signing with username={0}, password={1}'.format(username, password))
    resp = json.loads(r.post('https://api.mobile.walmart.com/v4/mauth/get-token',
            json = {
                'email': username,
                'cartHandling': 1,
                'botDetection': {
                    'screenId': 'Sign In',
                    'sensorData': bot_detection_string
                    },
                'password': password,
                }).text)
    logger.debug('Sign in JSON response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))

    return (resp.has_key('data') and resp['data'].has_key('loggedIn') \
            and resp['data']['loggedIn'] == True)

def walmart_register(r, username):
    logger.debug('Initializing session -- walmart_register()')
    resp = \
    json.loads(r.post('https://store.mobile.walmart.com//sc/v3/user/register.json',
            json = {
                'username': username,
                }).text)

    logger.debug('Register response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))
    logger.info('Walmart session initialized.')

def walmart_get_shipping_address(r):
    logger.info('Caching shipping information.')
    resp = \
    json.loads(r.get('https://www.walmart.com/api/checkout-customer/:CID/shipping-address').text)
    logger.debug('Shipping information response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))

    if len(resp) > 0 and 'addressId' in resp[0]:
       logger.info('Using address: {0}'.format(json.dumps(resp[0],
       indent=4, sort_keys=True)))
    else:
        logger.critical('No addresses set in your account. Exiting.')
        sys.exit(0)

    return resp[0]


def walmart_get_credit_card_fields(r):
    logger.info('Caching credit card fields')
    resp = \
    json.loads(r.get('https://www.walmart.com/api/checkout-customer/:CID/credit-card').text)
    logger.debug('Credit Card info response: {0}'.format(json.dumps(
        resp, indent=4, sort_keys=True)))
    if len(resp) > 0 and 'id' in resp[0]:
        logger.info('Using CC info: {0}'.format(
            json.dumps(resp[0], indent=4, sort_keys=True)))
    else:
        logger.critical('CC info not set in your account. Exiting.')
        sys.exit(0)

    expiryYear,expiryMonth = (resp[0]['cardExpiryDate'].split('-'))[0:2]
    resp[0]['expiryYear'] = expiryYear
    resp[0]['expiryMonth'] = expiryMonth

    return resp[0]

def walmart_atc(r,offerid):
    while True:
        __cookies__ = r.cookies
        resp = json.loads(r.post('https://api.mobile.walmart.com/cart/items',
                json = {
                    'quantity': 1,
                    'offerId': offerid
                    }).text)
        logger.debug('ATC response: {0}'.format(
            json.dumps(resp, indent=4, sort_keys=True)))
        logger.debug('Current cookies: {0}'.format(__cookies__))
        if 'statusCode' in resp and resp['statusCode'] == 400:
            logger.critical('Product {0} not cartable. Retrying.'
                    .format(offerid))
            time.sleep(0.2)
            continue
        elif 'statusCode' in resp and resp['statusCode'] == 502:
            logger.critical('Unable to cart {0}. Bad gateway. Retrying. Error code: {1}'.format(
                offerid, json.dumps(resp,indent=4,sort_keys=True)))
            time.sleep(0.02)
            continue
        elif 'statusCode' in resp and resp['statusCode'] == 500:
            logger.critical('Unable to cart {0}. Internal error. Retrying. Error code: {1}'.format(
                offerid, json.dumps(resp,indent=4,sort_keys=True)))
            time.sleep(0.02)
            continue
        else:
            logger.info('Product {0} carted! Response: {1}'.format(
                offerid,
                json.dumps(resp,
                    indent=4,
                    sort_keys=True)))
            logger.debug('Cookies after carting {0}'.format(r.cookies))
            break

def walmart_checkout(r, SHIPPING_INFO, CC_INFO, CVV):
    logger.info('Beginning checkout process.')
    r.get('https://www.walmart.com/checkout/')
    __cookies__ = r.cookies
    __cookies__['com.wm.reflector'] = '12345'

    logger.info('Initiate checkout contract.')
    resp = json.loads(r.post(
            'https://www.walmart.com/api/checkout/v2/contract',
            cookies = __cookies__,
            json = {
                'customerId:CID': '',
                'customerType:type': '',
                'affiliateInfo:com.wm.reflector': '',
                'crt:CRT': ''
                }).text)
    logger.debug('Contract response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))

    try:
        item_id = resp['groups'][0]['itemIds'][0]
    except:
        logger.critical('\
Could not find item_id in cart. Your cart may be empty or your cart \
have more than one product in it. Clear it and retry.')
        logger.critical('Contract response: {0}'.format(
            json.dumps(resp, indent=4,sort_keys=True)))
        sys.exit(1)

    logger.info('Found cart item id {0}'.format(item_id))
    logger.info('Setting shipping preferences.')
    resp = json.loads(r.post(
        'https://www.walmart.com/api/checkout/v2/contract/:PCID/fulfillment',
        json = {
            'groups': [ {
                'fulfillmentOption': 'S2H',
                'shipMethod': 'VALUE',
                'itemIds': [item_id]
                } ]}).text)
    logger.debug('Shipping preferences response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))

    logger.info('Setting shipping address')
    resp = \
    json.loads(r.post(
        'https://www.walmart.com/api/checkout/v2/contract/:PCID/shipping-address',
        json = {
            'addressLineOne': SHIPPING_INFO['addressLineOne'],
            'addressLineTwo': SHIPPING_INFO['addressLineTwo'],
            'city': SHIPPING_INFO['city'],
            'firstName': SHIPPING_INFO['firstName'],
            'lastName': SHIPPING_INFO['lastName'],
            'phone': SHIPPING_INFO['phone'],
            'postalCode': SHIPPING_INFO['postalCode'],
            'state': SHIPPING_INFO['state'],
            'preferenceId': SHIPPING_INFO['id'],
            'changedFields': [],
            }).text)
    logger.debug('Set shipping address response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))


    logger.info('Setting payment')
    resp = \
    json.loads(r.post('https://www.walmart.com/api/checkout/v2/contract/:PCID/payment',
            json={
                'payments': [
                    {
                        'paymentType': 'CREDITCARD',
                        'preferenceId': CC_INFO['id'],
                        'cvv': CVV,
                        'cardType': CC_INFO['cardType'],
                        'firstName': CC_INFO['firstName'],
                        'lastName': CC_INFO['lastName'],
                        'addressLineOne': CC_INFO['addressLineOne'],
                        'addressLineTwo': CC_INFO['addressLineTwo'],
                        'city': CC_INFO['city'],
                        'state': CC_INFO['state'],
                        'postalCode': CC_INFO['postalCode'],
                        'expiryMonth': CC_INFO['expiryMonth'],
                        'expiryYear': CC_INFO['expiryYear'],
                        'phone': CC_INFO['phone']
                    }
                ]}).text)
    logger.debug('Setting payment info response: {0}'.format(
        json.dumps(resp, indent=4, sort_keys=True)))

    logger.info('Finalizing order')

    while True:
        resp = \
        json.loads(r.put(
            'https://www.walmart.com/api/checkout/v2/contract/:PCID/order',
            json={}).text)

        logger.debug('Finalize response: {0}'.format(
            json.dumps(resp, indent=4, sort_keys=True)))

        if 'order' in resp:
            logger.info('Checkout successful!')
            sys.exit(0)
        else:
            logger.critical('OOS at final-step checkout. Re-trying.')
            time.sleep(0.1)
            continue

def runwally(username, password, cvv, offerid,productid):
    with requests.Session() as r:

        retries = Retry(total=9999,
            backoff_factor=0.1,
            status_forcelist=[ 500, 502, 503, 504 ])
        r.mount('http://', HTTPAdapter(max_retries=retries))
        r.mount('https://', HTTPAdapter(max_retries=retries))

        r.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34 Walmart WMTAPP'})

        walmart_pre_signin(r)
        
        if walmart_signin(r, username, password):
            logger.info('Walmart login successful!')
        else:
            logger.critical('Walmart login failed, exiting.')
            sys.exit(1)

        walmart_register(r, username)

        walmart_scheduler = BackgroundScheduler()
        walmart_scheduler.add_job(walmart_register, 'interval',
                args=[r,username],
                seconds=10.0,id='walmart_register')
        walmart_scheduler.start()

        SHIPPING_INFO = walmart_get_shipping_address(r)
        CC_INFO = walmart_get_credit_card_fields(r)

        if (offerid):
            walmart_atc(r, offerid)
        else:
            walmart_atc(r, walmart_get_offerid(r, productid))

        walmart_checkout(r, SHIPPING_INFO, CC_INFO, cvv)

        walmart_scheduler.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help="Your walmart username (email)")
    parser.add_argument('password', help="Your walmart password")
    id_parser = parser.add_mutually_exclusive_group(required=True)
    id_parser.add_argument('-offerid', help="offer id",default=None)
    id_parser.add_argument('-productid', help="product id",default=None)
    parser.add_argument('cvv', help="credit card cvv")
    parser.add_argument("-d", "--debug", help="Debug output.",
    action='store_true')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    runwally(args.username, args.password, args.cvv, args.offerid,
            args.productid)
