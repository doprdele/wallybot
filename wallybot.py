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
bot_detection_string = "MzAyNjc0ODc4OAAAAAAAAFXXg8BgkuDrxgjNhfKFspIs0qumzLauUgIxU9iT96GX9QO4pFwYVK1Pa3cPV6fz9p4VvsAHldmnFEkm\/FPZyRZKNDk0eurY1cjwGaRhoqNH6McNCPGVitBvO1NFQX+djyQTmJJnR6EMAEsTvGvyMxIltEWLyqe5kBuLoriGMXPppb3qWu1bA2X\/cyX3SFh7Nb0Dd0Dz6rz8ShRA+2c5T5k1Wf8CiE0NGa8YczXyVjrHeGWNKstqqpLf7jXCZP06cU7fZ0SrgrfayXGdkNvfpuYNNQ0wNvpWjmkBccWVEYhmg1e+LxBMMT6DkyegWubw7SmW\/AQbeSnf2XW3QlT4i0AB\/+MLqk9I2FTBEmYl43PvYy60dxAbsrwVEf8V2Kx4pcxNxaYsjyitpylA4IjWSTt52XX17VyrZNbWn4Dr31KzlA4d6tkTg0jMHkaD61LtgzxeU5N5zhXWTQ6HNDBSV3hhDMZ+kQfnSASPOYLXXPmKwOWnvQjBtp0IXVc7Y4u6w\/GGGlg8jHoLSKLdzybQVFu1cVLyVyi3yUG9RsLEuZd3IC9cXsZtsBsQNp4fRc5xuNN5OTgtS4pvftQ7yN0mKf2FmaoM+lUCxBSL5A+k\/PbbSoVBlSvFrX4F6AoOYqnUrblg0dFYLxJa7faqtfnOehv\/\/L373xOwmKdTRCfFcJGe6cGUqh3BdHww\/chXd3Tp8ZZ7Sr98NxKgck1vTYjcO7Bf5LldFfVGNqkpXo3\/wKab6QWDCzOHTkCv3fvdcKhoZ9vG2x+ZzRXye227vSsuOvNotsjxqqgxOdh7vBTsR00+3jDoqpZ7sOy7IoVzOC\/NSWP4vUdOov1xZZJ0MawKxzuDH1wffFb6tan6WYiJs4tPmy36uOG88+TSmBq+wibeG+e3T4gYSWVc2bv2OC30y0vm3E5umM+ViL6Iw9FsoUqHJuv1TxOePitvYfGv8mLCOO1AvMC2LCM6SkGAfOt3M8GjATYFVqAtT4oETD8wZlmCSQA1NseY6N0Ia\/+cTa81TwB9QRI5cmihCNJZKt3+MmEHqHVh3oQ80A4wALS4K9ERaIy3F1znI4sLBkS3SIPapzJcLCEwEpmwxYhPVxxHKJc6\/L1Zkpw+JNteU8jDWAAVoHwkM7Big+lvWaG2q1yuxAKHGipekX1oLh0IxfAuiVVnPlAkWj0hbS4jspYSCgfk526eUmWY5NzRby\/hPmyXTfLw+M\/VGrE6XFQ4+LhZVseS8su5zAgd\/p2+CZLvNOtG2cv5HWkikqP9Ho7sAXhkFiEQSP3WzXG8K1qaJfTLduOYpZ+69BRSNEFn9cgRX7e9yhLqo6jVz+q2yCBFVZwE3W46wS42xU95NWU+Jz7lHMrqjWlsEbPyRvfnsEOmHvy+zasN6+YQrTOnjkKyNiGa7gG1gvHwsKOLKzIMb2EgPROI29kJ0jV3fzDR6mrY9VBINP0nLnpDmH73kaX\/aBCYS1sfNKPgYZkaHNsoRxnTJ\/AW9OebA+LjRX3GW3t9z1alb7uX8kY4Dy9pZ3WiOO+N8umK5WTpEUVvaCfLO1xT9kszhcUUhupbU7e\/Fa2wtG3nStSPxps+M94+zdxj1LgbefaF9zwhNZACy7YjW3KhCDEtzIVwxTJJT1vlV0AuZHVJ64ZVDq2JEU3QD7YoXlgTKJBzOWC4iAXahQQPp23vAm2kr+5Z6pUkDiq2GMSViDP3ludaWGlX7UhF8b4p4t1NJFu3QeOAps4\/a+0KGsQVpFV7zMZBYUtR8tvvIXjX9zeK\/7N7V\/2EjcHeXwwATZN60FhY03uyEhZ9T1t7QRD+0L3Rz5lxt2m1\/tPX+RwmGSQWuqMu4kESCGirrStdKCdcs1JmVpYrZrbY0HCzXHxwG4sHEfXQSMUJbtVRT7PIvSb1lEjgzzKnRSiYlzX4y6O7NPgtd36CFt7ZuS1DvhWT\/\/jvd0tLPBgCkw\/F2z2YmjzQKbT1okyBT3x7HO\/+De8HYZfMPpCPeNi15IgRH8kSPPkHopih5ZjFakacwst9O53qv1tYA4XQisGGvmqvmvCPCDq9WMZKK3mapkeJ6BfkPlT44OrwKBLbBT7sYJx5G+8m+YyZQ5cKE8MRthhD14DqcP9McYfk635NZKjC3evPiLENJGDwfmU\/EbsPzkgOFgVnG8K+\/3HFOOD+XcJ96qPV8jeemixnnxu30I4ZehAsrorsTxT+3nRircxziJIyt270onJVqsyyD9\/xSWJZw5YPjrhYOiJCSBbchOz9KblDS4LERhvWAvxKl2d09HwXDrrGTe4u9MGztpwoZz6T2Tj8PamlT6GCTwvygbzoC4SCu2jSQ9IMzmq5xrx82heU5eiD3LgcJpu0jBZ6zw0vPBvg06RIGxGYc2vAzKBmiQmSDcYZ\/AOsQid5ZQUD+eph1DrqhGU3MpuODYNqeoIZ9DeFNikLLJ0chveflMeetAFCi06DOZVeqi3TxtFRMPylcZ+jge5ilfJTUnpvH2jB99AHUPgDmghilfmdzzfCI09f+PwbZkC3GIMHthtFqtYN9KyfASTejLQuhpNqbQiqtlYOI2DUuvXBlmzPjtACIIBJQ21C\/A5qkmoU8bwOgd5oS0bGlNYJplAz+5cj\/+npbWdOFtzUo0fmXL56oCb1fvDXdMtFW3nWW2CR0xlJ7YIQvSOnVz5mu76P9pn1Z+0AHEMQGdiYscBxatoRTIU6Y46Q1cmTpw5UZTfaFbKU3+edeDbGrVuQMK+Ezu7m2XQ8lTu5OFl5Gk3G86ZzpiDGAMyNJ1dg1INgRQF+UJdGQf\/V34yA3qLlEps4NcA7+ffC1qqiT\/HSSMqZlweb4RyVITC1t\/klkDnDizcuXqcAFppK0pevYm2RAZ\/ccnA3N3fOoY+E5QMFcotSOnzQBlXwHiU28PfTJm+uetwo5JC5hFn4ncT440Z13C6vt8Ryv4h\/CdordHW+\/rxsdn2Wk0ug281Dt+Tp\/rN6vzsz9Pj\/Mrw\/w1eJYmRiUBcFw27XWi791w4SWeaDxyS15wJoliZKKjE2pLZ\/uybOHXcgI0+EBQLxs9XnB4won\/HrVr54hHGwSpz+DW3rhnrH1Q+medOgFGwlRq09c43ZNmcKtGIsnOxvNLVgAuhuWmvovudC8b04iPwVLvFeO7Ue+UngSi7xT8+xrHehLj5ibTBDrofa9TQW42hvP0mrEBdXB4MF7im9ljihog15cfBXDuj7hrrbe5kPbS6fVW63YBZ75zt\/y3+y2I4cd7pEMtWo3X6OseMokbpKnVS+U0nNMGfm7FWB9Hz2m77B8TSa7okMrwwYaIKrKDa2qRf0LpJhm2T2uVeU5l0lJknHvo9nrmRFG8raUrcOR4CSm0EgIVzFTfJY2pmnm8XaiPkHC7FuwmvE7cJV6k9sy3N6JfWwy7m5MMkcSITA3EBdoJIsf4tpAFEGEdUycxFvWZkzz3zGBETHClmNGCiYJIob1wZWdYIe3Y6giZBlJtWEr5UckqpBIvx41EvEE34EJiJ4HAW6q5TpnzEt86qfFhp9FI8DmFOiPz2GduRQG+IGmoAU21gcl\/09RzuUxkyDDqfWqIuNgTmOnW\/luWhgaphzVNfPsikY8KoBrvkPeqc3ZVX+gn+XLiLMGXiQ0W2A9Uj2hGklfU8MPo3Ex8nETWbBDRAb9Ty0pKp5FVBu8brGkmN+w97WkZzLkqNeteiSb4xOkfZc7oChtu8ENiW71sGYJC++vubt+s80NFhXuRxE+FLo5gU7P83NGDnpkmMvGYW+aaLtRAunNzcvJk5Gm58cA7gA9GIEP51Se4a2Qk+9Z6axLU4XlA3RSUI7ErWRuw+Xim0fwDWvmP+MCBPPUl9lLN89B76trTFGCyXazEXv9cQr64QXGM3CIHJ5dtTM5UBOklnFg3H5Raoh11srTd924+qAztrICqN1EVAWj41oRZmphs3HPMPxvIJobwjjJDDsDkXnslD35u1d8n0\/\/UYNlwcZlMga0ZN47KF6k1d2AknKs6FgGddTk5VaTdn1ui6mB1EojgZQ5BuGGC2SS2uh+Hxo5Lmt\/nPrSVlYRML82BE2iHqOVx+KXF81lmfdEUY7Hk0wgfc76hHvLNCJWLrXa\/XuEHIVOTqNkbrZ0u+he1wQ73mbOBjLioTvo3nRzrxXOVBF93OT76mBNjheZpJPaIT9LRGcW1hQ4ELkfd5rtOMqVLiCFGhAViRPGImb6khEqqCfcasiwqB\/pENK4YKPAdxlBOWwSpt6OEmdVc\/Up1RvrF36cjbEBP0eC34b4ArBrkGrTTcVpVnydqVEzeC5DlFJjdJdgAJA2H3mnSog+npMJ2owkpWslmX82F+7Qa3tNuTUl6exwUE\/JtII5fJMpf0EZZEavuvaUb\/3eqmNi7vyo8RYlNCTMbZLFNg3Y+ql0V7HZOHfLrCWqS7zGzdcf59dEeNvocPLIjlGwFMwiZ1u3u7GcZFZDrwuj+WTOZBxNBi3Uugpp36uhxTnGdkdqzpWY8LKqpPP7CO4nXB9LH7WhMclKSwZn85qNVaVw71DiIdperV9EFW+7o\/YzhnpuMzO0x9IjrG9Eqhz7lirWF1hQlJZxWQQiPh+\/ghG6mrGUNI33+mXjRk4BpzALixRkQ+lGvTbc2OhqULPZNBD2SyxxVpIr9Ly9DubdzJzQCh98zMHXiE9OUDgFiPf3SvTSI0vTJXG9Joz7DcEAGHWxfb24uGnCfGkeBq1w6D47Qz3bUia90+Mig1F4lMdQxv0DhcNrhFpPmX+7YZx9kZL0e8Jb1SJvNxB79OGAnjKLPU7bQycF2L31nKXURODLXXkWuroiUrELBNigaj11D7N4qSHth8otmjrGu\/mb3FCOPAvMfenEK4Jd3od8gyqp6Jh3y4xFE7qYGHYdvm78x5mYkbpZeW4P5pu9d+5G\/LVFDgAypmxU1nOGZ+EUiROBisJjVjfq9am7IQANA8Cg+PAFF\/O4ewqa8OTQ95EQ57jqzQrpr2x+Af1axj7lTwjnNdBajqrjGnOFZuIf\/rndtCtnN\/WhswW9m6z3R\/pP17SH2+iCS\/yes54IAyZUL5lbi4W9uFugD3abYSvxWRQGuM9hGu3lqaX37eoykgBJJUix9crX+ZFdL0ml9eHcCiXAL1EbhtCXk0yXx2sSo8vHE0vHCcTazd3i7084cRU1z40RT1BGlBydYBtGF6EY0DhlB3nNyw2S8qmG6l24GmICAi19wOuvYfaoxvcMSsQCI2h3wOPYyhOh96zVpJh+aZjHl7sq5PQuKyt0r9p+\/gCKRJ1WT2VtM6danPy1i+EbL0e0a6YeXEEB4NAEAdVJDHMt0dJ9\/8etpF5T8ccTZmBDL73gy\/KFm6il1b+PiLo\/bdV9\/NLKvY1lImGDsmuL0f7sDahyvezfr0W+gdetkfoJ26R0LQq7HB+1Je80JjYffkKY6pHvVwWobyDqi6pAi0Jy2HuY\/lNAMIxyfkYQwcMjt7Dmz\/3DizVz9u3tUp8anq3hAZAUFiHiBuAGJXOoug7wF+vVFYzzgyIlyWRbchuYo2lOTy0mIXSCH8uahJLnJ6F+jM01q0229fS6bf8St6nfF02JAqbWZtF7UdRIlwCvfXPI3Yt4zXHZwNaz\/SH1XvcLnRN+SpIwnitz8IwxhaIQYo43BEr4gXShA3zdq\/mCSUCoSvmrqxvjWFI4KiZVxxOUFPF9mL7gSEN87nZz6p1pzt4+pKC9a4OQzS7Q4T21O5zWxctw2XAJDDIoloXO274jtwd6QcRE3hwJmLnO2\/KAqvAIQ1P9yHxN5ee29JWo+wSAfxVcYLUPZi8ygUk3jJyjT4hpvu45XoLNsMMYODgONjz7TfZQT4XE0hJWOmGumJ+fxwZHYnU4SxrWqeNMfKbIfkmH9kWAv+jaaCbR394J6Nga9tprWnoswkwJwO5490DlNylf3Hr3ZUsHp4IFuVGOvdEin0b+Xf+2kdgsmj4IsW\/RJZP9QqR8c15JsccUZDUR90FBGJo0Qy89YGt5wsFNuf8MPxEMg\/\/YVnpdibm5EDJSIVX9+ypfV3GKalStl1UjS3OXCt3hDV2VprHX4yxdlbfM2ui0eTUbqo880cEevjbK5tZJ71jxchBiA9s0io74NBPAZG020UMYAuUVHXv2A09XCdpbh0fhFd5oktfcLpm\/0KudHL2KkNw41uGyPkR11oVjnipI92Ct6IOYnRdAf7y778ZCdtWuPIAo7FVuu+aUDHPBbGyIDbPJ5tC8b89h\/Y\/7Y7OPLOifdEhkMe9hxMjr3zNoRk9pVmUHwwO9Q4r6P4e+l1WdU5bCQT1\/KXXmMYnVRZVNMrv9NIsiQIiIHSou1JQAUggp76oRzaL78FGWdO7ieFhjVNV3r2gEdjY\/hwegzDYyreWZtjCUhwcTgtW1qjQR+v8LSmO39EBPEIef4WbMpCBEXbfjb5h+yDZQBTPJKsqjcHb35oIi4SJrasKURVRq1kgyrSUCvM\/6gWxco+PPWC+xoSSHp3PiEeqMaVLkSdF5k+B9LVOhOeIhPJSjITV6Xvw8RADp2Vew94+cHAZ00MU+siAhRa6OwQi33tTVf5LaVaQ7Zqj66r9MORCLt1kQ16suuqR4MuchPk9uorM2PET1BVHcL23Ot4t\/qjb33tIBXdE7nct0BefTuJrYaKW2g+0IoWF3tbPP8HlWsc6oWuqcmXwluyOiQHIvdqtQiaOfNpZO5QfwtfVhZqlwOqMAl+yPCcpqnpgeHgfu47HEeR5ZEHiVw51wPWDqKgEEhrWEXPjfF8\/EEZLUqfEs0R4ibk+BPSJBkFtjBn6xZk77cqNMyJ80y3UY3xxkOfj5dzYJaa1KyY96z8fCv7v\/xKjE7RZGnk1M4bpusCWgztzQlL0EkNruDyytdL6QFepSdBb71kIE+fyWLnTw7LrHJpB7e8ouXmjFsvL11Te0cshmPLCTCvi1+YMcr+0PAeNIyEd4B9ZkDqTF443wKVrFHr5jig3SttLP4cSmNnwJeSNbbC1zX\/KwGHGLeEzpl5Il8kln3hS7gXeVLopl1k\/yQk6XBB7SZQzV4XCep78RdsVJNP2MfV87qO69y4UEckDnvJ\/NkgvxR1AMI6nj5i25qCU1uQ49fG7B60JgTXJMNFOaugvNSJb+WTFKAZTls0ArSYxLr6o20jhatlAwo0DyO4m0JDyqk0PHzzUFGsi2Xp0yk7hFfnxkGlYY6YckIAYuraTRVgpgjqrduJwmh1874Vynz4WklQoBrJlDjH1ZLeyOVXKv9Lpz2dq\/VAphH\/lN9hlAab7o0FijqbIyYG\/QMl7dQ7DjEC2N54MNe5hW1x7uMllHSu29uJp5w3cEOUp8khimTwT3MBVH8O5ohVusAGKG5q6wcO3dcZjBQySkHxFYEMZmenL1WXQ6wb4lEkM\/+aUbG7spI9vkp5dMgN0PE5zG+M4cq\/acA5MycJNy0pM3WBYhiMu42Ze3K0iL2WiQIyokFBhpPJd56qmHFW\/bkMvw7jceloGKW5FyOPlFUFxwC5Ov0hGFIIX7sbSlaEhSMdVKNcWT0fFoE5Rgsc1Ivp\/eC6Wgj6NM8n4O7mNz5\/\/BzjcOEnezA\/n5QfFwTtaqbbXAV2Kk9SGGMBwnLp21iHtaf7h55Cz1WKkGglnF4DqQgmGoABoz4\/ax3kfmwGnOuDSnh7mHLqq1lI9B213SlxPKfhuru+t4ntuX0X\/DdkXiRVitrdhBV5Ma1DjUHQRK77xV9uT\/YZOk9oXhhELpCUZ\/RcqpQ7kueNoxmXKDaQEc2eqE7DDj9ll+65XTIZg5MlFcJlZGavlDl3Fon7nEzLE0T46XMHe0YWU+f98RzfspiAgJOBO\/I0+Rlkze\/XSgNXCxH2ejjpak1pEOv9aSV7ShJoh8P1qcajL1ssjLmflYf97n8zQMbd4F2ZCrg3xyPljitEJrH+k05iAbHO5ifultGm8OlifaTfBT6\/he10LezizAiobbRllEETzgCITFKalxCBZBkx6dnyeYOQUQ1jtDXLIaYT6M6\/K1nVHunT3GkaRVHQhoLwprNvr\/ERORbd9u9xlCRgXUN4zsEWwhHTJQY2LiplruV5C20G++6sLIn\/XwhxcKR5ta0fSYQVVMmI66Paujhp1amREDjv+rg3YTl8Pq28DEVWnJ8Tn7WZmz274bowkLXmUNkz62QL3SHDzbSUiQH\/Y3NiKQEZBwICCr1JfCp8R\/Oa3CODnsA+vMxrmOe4aep3XRiuqyEBa2TUiUdyouZehbusl3\/ShQ\/Oj7TnQR4im+JRwYb4JmcrIP5SO28iTikwZJ\/a+VlvmFdSZRR6lQ2Tw1cApt76MqbMejs7S+povlyaABCEHX+4+fw7DPY8UcvBP68y78u41ktexR6s+jj\/AuN5qaSDiey1KDk+0MMfAL9Hauy78m83Bm7pQbkcv+netqqBk+vO4FlUc\/WG7iQyFxA7FG2Y51nwDvG848DN3nMJjGVriHa+7YkpyV\/OKczPof\/29R0dq\/nGDtDqzu4H\/Lir6UDznwKB3GP6BnER70IKnoGG+J4NYbS9vKVjUAgdAV9kh5NeY4G8ciXITt\/HvBit1uxjgH+bFDmq8wx95NbZoN2FGcYmP+a54O\/aGpRIZo9E9xC\/+XewTY5CXvy+SFA1p1hv4otN7cPleL8On4L3X3Eg7qut+Lhs9xv1m453w8u7RW7s2E5SvXSeimmLcKq2bn0ipyQhLBco8w5C+LOGLlhMZ4ipHVBYvFQs5nP6OwGmFEiJaqvd\/QWvW+HuKdfFvh+9OK2eRds142lZJgPLwx+tsi5y4tTsP+pvAzHtg2AYnwFSEKBH\/m8qdUCtsR+G9Eamp65MeBbJ8gddNp2Vmf5GiYCKEzCZlBmdOC7wBMIQQm6Lj399kpyo40vCrZYKZ6z\/Z9xYasRoWI+AWFaZG8jpcP87xoPPL+u1ODNMcfwFYYzAMCuQILesgNOjlRCZ8y3sM3lx8rqNPfG9uMPKCJpsJDyOV3Hn1LJqiB0XD4dqZcbvR2pTKPkETHtxZwztIAxCMpCtcNQ6SLnn7JbOpspca5FFgsazCtDshBlS11Aw6jHxJg44+G5TwIDvz5aB3UZFWgaTbn4fn42UircmXsjkAmvcFZy4Bk9m3z5umfpCQoJ6fHA01scGV5+ir4ljKW5SwCBEhFvv\/ll9r5O9PxqZLrhl16FzfLjfWTpD89s4w5RgeADswMZY\/xNi7ffxWOgGl6O1KOWzsHf+5w6sioibHRJogteHQXmUH\/8ewhr7C0OHjdavyiROl\/50pNaIUKvpUt8XVE4PNqDwCTk+v\/w1R6z0c9gWeSi9JK\/6haiCoNUhxWedtb1VAmbsitufdX3zSd2ykfVzbP4rYP213AjrxkTt3wLklXWIOjnOJ5pPN579tPuQxNH1Fzlj8P3rzQKqCBF1ZdQEIxm9lX6y+DFXqMXh5hI+MCS00PxFiXGXaXLL+ScteoLH\/D6Yet7datpb5weCaqftOqXZt1f0WTWTDKNoN1qQ\/K2rp8Y7ZBpaKrfkwp\/02bQAYtAr0rEr9ZDrckhrWoTnWOvGl9T78+V0+n3mBZr4SaSdFfEM4zH3OCXKVq3LzLecptLkY5F8AaE9senM8WAJiQvj+IUVMdbrvTijoYyrGfBglpeQuGHtsMUnrXDSGR8P0nLgb4O7hUrZYky+5g4kTV18WHJBqLU3uyqB9+C1+sbFqwQtSIO6MgaeTCpV7AZQOJQbC4FZgmPmywUNFnbzPQzHYP3brmjNtHb0tBQUAX7B1KXpCVLB1f70xmag7joEuMHl4CHFgJXsBAuHFADVZM\/zKKq6ihVgZsKcDw+CeGHJnFuB2oqGEnvxqaXfucohJQo9NHYxHiTP8Z0XdYQQAfI7tYMQq\/SUM07xjtJ8IuFHvbK3r87R3ZcmdmWhUDuEPRFV79s\/JsPDjicINUM4MgLIVoSgjA42Y6lf8lwphgDDgC2RdXhQU1hvQ9nhsgJPuBDAvDiKMwAe82F5AfIv+YtJFD5P8m5Q328rS3ieqLCioOoz3EcAU1bZWJy3jvhDUt6TKuM+gr2EZrMRs4Z7DQSmLGSaZFlrN63LwjiLqTqay9dswZjQg8toxyu2fc27AmziZziP5faguVC50FPCdT+uj0PdxFMxhGcPhC8TYrA0FNssZuMIFo2uEbWJya7bcUwCt18HyDVNo1U+EJh9JIIYfLv8VR82BPMs\/qoOFQFzmd\/fUZ44ygmIUWWU41B9F7fZmKm8uKz3ncNakqY2sNHp\/D5tYzh9sZYVJggM1xKk1p8aE85pQpfLxg2AxgQf1DsljsPjZxJFwcT+5gGTrD2lra1QE3I2MLl69V2QFw+BHDu6lujc=+060+069"

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
    parser.add_argument("-d", "--debug", help="Debug output.")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    runwally(args.username, args.password, args.cvv, args.offerid,
            args.productid)
