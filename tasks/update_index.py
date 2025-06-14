from models.user import User
import jwt
from logs.logs_config import LOGGING_CONFIG
import logging
from schemas.response_schemas.secured import SecuredResponse
import json
from fastapi import FastAPI
from sqlalchemy.orm import Session
import requests


def update_localization_index(db: Session):
    cookies = {
        'external-locale': 'ru',
        'wbx-validation-key': 'a05aea94-1f15-4a6b-a879-91214ab6208f',
        '_ym_uid': '1706558827848753951',
        'wb-pid': 'gYFVNmiV-ClBWLbziF3mRCivAAABjuat73-NyqrV1SGWhaUffhp6Urcc5xtuxVL0cGUy919g2hV-zQ',
        '_ga': 'GA1.1.15166272.1716875082',
        'upstream-cluster-uuid': 'ru',
        'wb-id': 'gYFGSCFJ3zlHoKwPVBuDkd8NAAABkhrt3vPPKMFKWRgBJmzE-Ug2NVmCf-QNFfUffIuugHxihQbPkmRlYjc2NWFjLTcwYzAtNGY4My04N2FmLTAyOTI3MjY0MjMwMg',
        'locale': 'ru',
        '_wbauid': '9366149821731088077',
        'cfidsw-wb': 'WWHCunH5Nmc7GWW2QYyk2p4gerlt+bx7uegVeivxBxV7uLE4wj2jYMYjltVbtJBxsPiRANVnaIqHSm7KwJDq7URtNZxYO7DiwCcVJrhYLaGqs1d5A/hGNgcmJNkNO/lmLzrKX93nw5U4fOZO13JvF+p8brXQ986AUiymq8w8/g==',
        'cfidsw-wb': 'WWHCunH5Nmc7GWW2QYyk2p4gerlt+bx7uegVeivxBxV7uLE4wj2jYMYjltVbtJBxsPiRANVnaIqHSm7KwJDq7URtNZxYO7DiwCcVJrhYLaGqs1d5A/hGNgcmJNkNO/lmLzrKX93nw5U4fOZO13JvF+p8brXQ986AUiymq8w8/g==',
        '__zzatw-wb': 'MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UxQGgkaEdbIzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwcGH1tKlULDV0+RmllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVQCw0ZcXR2eFxsHx9jeRUoTFlTeSYhGDEpWAs9QRRwSl9vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwgZk1bJklZT3smHw1pN2wXPHVlLwkxLGJ5MVIvE0tsP0caRFpbQDsyVghDQE1HFF9BWncyUlFRS2EQR0lrZU5TQixmG3EVTQgNND1aciIPWzklWAgSPwsmIBR+cSVWDQ9dP0Jzbxt/Nl0cOWMRCxl+OmNdRkc3FSR7dSYKCTU3YnAvTCB7SykWRxsyYV5GaXUVWDo+YnBCcywmP2YjGERdJnkSSjMsG0V0JytYf0Bbb0dvLDA+VxlRDxZhDhYYRRcje0I3Yhk4QhgvPV8/YngiD2lIYCJKW08IKx0ZfnQqS3FPLH12X30beylOIA0lVBMhP05yASz5mw==',
        '__zzatw-wb': 'MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UxQGgkaEdbIzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwcGH1tKlULDV0+RmllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVQCw0ZcXR2eFxsHx9jeRUoTFlTeSYhGDEpWAs9QRRwSl9vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwgZk1bJklZT3smHw1pN2wXPHVlLwkxLGJ5MVIvE0tsP0caRFpbQDsyVghDQE1HFF9BWncyUlFRS2EQR0lrZU5TQixmG3EVTQgNND1aciIPWzklWAgSPwsmIBR+cSVWDQ9dP0Jzbxt/Nl0cOWMRCxl+OmNdRkc3FSR7dSYKCTU3YnAvTCB7SykWRxsyYV5GaXUVWDo+YnBCcywmP2YjGERdJnkSSjMsG0V0JytYf0Bbb0dvLDA+VxlRDxZhDhYYRRcje0I3Yhk4QhgvPV8/YngiD2lIYCJKW08IKx0ZfnQqS3FPLH12X30beylOIA0lVBMhP05yASz5mw==',
        '_ym_d': '1739104555',
        'neuromarket-captcha-token': 'MXwxfDE3MzE1MTM3NzJ8QUE9PXxmYzk0YWNmNDNhYzQ0ZTg3YTE1YWUxOGVlMmIwMjQzNnxuVDJRalBkNEJ6QTFwczF4ZzlvMGpEd1ZpSWdzZTdCUnhsUUNYRXBtdUNS',
        'current_feature_version': 'E598F9C9-A7B9-478E-BBCD-A8B4DAD79DD9',
        'neuromarket-token': 'ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBZWFFpT2pFM05ETTBPVFkzT1Rjc0luWmxjbk5wYjI0aU9qSXNJblZ6WlhJaU9pSTROVE0zT1RBeU5DSXNJbk5vWVhKa1gydGxlU0k2SWpNaUxDSmpiR2xsYm5SZmFXUWlPaUozWWlJc0luTmxjM05wYjI1ZmFXUWlPaUk0TXpWbU1tRTVORFJrWVRrMFpEY3hZbUV5T0dNMk1qVmlObVEzWVRWaVlpSXNJblZ6WlhKZmNtVm5hWE4wY21GMGFXOXVYMlIwSWpveE5qYzBNVEl5TURFekxDSjJZV3hwWkdGMGFXOXVYMnRsZVNJNkltSXpOems0WlRnNU5qTTNZalZtTjJJNU5UWTFZbVUxWXpsbE9ETTBZbVEyWm1KaE9Ua3hORFkzT0dVeU56QmhNR0kxWVdFME5qQXlNR05tTW1Sak1tSWlMQ0p3YUc5dVpTSTZJbTVDUlVWaFZVZFZVR1JQV0ZvNVYzZDNTM1U0TUZFOVBTSjkubVM1U1U0Wml2TXhxQmxnT1MtdVhlU0pEWUcxeVdEOWFraW9vSDNkc1FUaVFlcTZQU3FITEt0MjE0RXJvRERDcThacTdIaXNDdHBJMk5kMlBYd1NlOGpQRGVOQzJoSU51RUkyalBjMGRtaFVKbWJfTVBKMUxBRzB6aDlIVTlXUVdLeDE0TjFSYnktc3J2aVhWTTd1bUZMdjlzWHllRjIyU1lXTGRvT0VCN3FhejBwVDhLaFRIU2hCd0ozdVV3NUQwRFNBclR6cHZsclY0Uk5VRnVYNVZrTzM4MElUMTR0YlJHNTN1QnZkdGVjM05HdjNFUnhrX2hHNHVoUGFIbXJsVWZJRHp3M0tFQ1RKd1JaVDNoU1NXc3JmZW93MVExRE1nZlhabHZpNy0ycmFjZTdLc2h5aGhjR1gyZFVmWkpBX09CNnRFUmh1SnlvNHRpSmFjVUp3aGtn',
        'WBTokenV3': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDM1OTA2NTQsInZlcnNpb24iOjIsInVzZXIiOiI4NTM3OTAyNCIsInNoYXJkX2tleSI6IjMiLCJjbGllbnRfaWQiOiJzZWxsZXItcG9ydGFsIiwic2Vzc2lvbl9pZCI6IjE0MmZkYzk1Y2FiMjRiZDk5NDYwMTg3YmZlZGZmYWM5IiwidXNlcl9yZWdpc3RyYXRpb25fZHQiOjE2NzQxMjIwMTMsInZhbGlkYXRpb25fa2V5IjoiYjM3OThlODk2MzdiNWY3Yjk1NjViZTVjOWU4MzRiZDZmYmE5OTE0Njc4ZTI3MGEwYjVhYTQ2MDIwY2YyZGMyYiJ9.QY87TYUI4FD8CPWhvmuZ-8S4kOs76L6g_9h9nESfIMvSK1HQV9CcfwoiGSHPEQ3Ucvi8nbvhxGVcAl7N0rq6EIGwDquhjySFjoHBTZ_8gkxVbHcWn4-2peqe3_cqL7ovXTv6Qe4R8VdzpgTMFsruFx0UUg37ZJm5CVHR0YbqZq22EbpAP-ZWxX-Z3Ti9WpBbfwHIDD3hIni0lKO8g_iiaQU8nAu5x6AdMwgMoZNgP7XLEzZPFjyZnQRNInydmv-vyAu0CQ7TBB7p_4rhaXCejqXxO1_w03L0dH9dHVfT1HK4UMrSaHRrIaXrlLfgt7gTjNUgGrltYHCSMl9ZVbyFRA',
        'neuromarket-auth-v3': 'ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBZWFFpT2pFM05ETTFPVEEyTlRRc0luWmxjbk5wYjI0aU9qSXNJblZ6WlhJaU9pSTROVE0zT1RBeU5DSXNJbk5vWVhKa1gydGxlU0k2SWpNaUxDSmpiR2xsYm5SZmFXUWlPaUp6Wld4c1pYSXRjRzl5ZEdGc0lpd2ljMlZ6YzJsdmJsOXBaQ0k2SWpFME1tWmtZemsxWTJGaU1qUmlaRGs1TkRZd01UZzNZbVpsWkdabVlXTTVJaXdpZFhObGNsOXlaV2RwYzNSeVlYUnBiMjVmWkhRaU9qRTJOelF4TWpJd01UTXNJblpoYkdsa1lYUnBiMjVmYTJWNUlqb2lZak0zT1RobE9EazJNemRpTldZM1lqazFOalZpWlRWak9XVTRNelJpWkRabVltRTVPVEUwTmpjNFpUSTNNR0V3WWpWaFlUUTJNREl3WTJZeVpHTXlZaUo5LlFZODdUWVVJNEZEOENQV2h2bXVaLThTNGtPczc2TDZnXzloOW5FU2ZJTXZTSzFIUVY5Q2Nmd29pR1NIUEVRM1Vjdmk4bmJ2aHhHVmNBbDdOMHJxNkVJR3dEcXVoanlTRmpvSEJUWl84Z2t4VmJIY1duNC0ycGVxZTNfY3FMN292WFR2NlFlNFI4VmR6cGdUTUZzcnVGeDBVVWczN1pKbTVDVkhSMFlicVpxMjJFYnBBUC1aV3hYLVozVGk5V3BCYmZ3SElERDNoSW5pMGxLTzhnX2lpYVFVOG5BdTV4NkFkTXdnTW9aTmdQN1hMRXpaUEZqeVpuUVJOSW55ZG12LXZ5QXUwQ1E3VEJCN3BfNHJoYVhDZWpxWHhPMV93MDNMMGRIOWRIVmZUMUhLNFVNclNhSFJySWFYcmxMZmd0N2dUak5VZ0dybHRZSENTTWw5WlZieUZSQQ%3D%3D',
        'x-supplier-id': '9cc7c16a-416a-47fe-b72d-d890e0b62a73',
        'x-supplier-id-external': '9cc7c16a-416a-47fe-b72d-d890e0b62a73',
        '_ym_isad': '1',
        '_ga_N5X7KR2NQJ': 'GS1.1.1743633771.165.1.1743633789.0.0.0',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorizev3': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDM1OTA2NTQsInZlcnNpb24iOjIsInVzZXIiOiI4NTM3OTAyNCIsInNoYXJkX2tleSI6IjMiLCJjbGllbnRfaWQiOiJzZWxsZXItcG9ydGFsIiwic2Vzc2lvbl9pZCI6IjE0MmZkYzk1Y2FiMjRiZDk5NDYwMTg3YmZlZGZmYWM5IiwidXNlcl9yZWdpc3RyYXRpb25fZHQiOjE2NzQxMjIwMTMsInZhbGlkYXRpb25fa2V5IjoiYjM3OThlODk2MzdiNWY3Yjk1NjViZTVjOWU4MzRiZDZmYmE5OTE0Njc4ZTI3MGEwYjVhYTQ2MDIwY2YyZGMyYiJ9.QY87TYUI4FD8CPWhvmuZ-8S4kOs76L6g_9h9nESfIMvSK1HQV9CcfwoiGSHPEQ3Ucvi8nbvhxGVcAl7N0rq6EIGwDquhjySFjoHBTZ_8gkxVbHcWn4-2peqe3_cqL7ovXTv6Qe4R8VdzpgTMFsruFx0UUg37ZJm5CVHR0YbqZq22EbpAP-ZWxX-Z3Ti9WpBbfwHIDD3hIni0lKO8g_iiaQU8nAu5x6AdMwgMoZNgP7XLEzZPFjyZnQRNInydmv-vyAu0CQ7TBB7p_4rhaXCejqXxO1_w03L0dH9dHVfT1HK4UMrSaHRrIaXrlLfgt7gTjNUgGrltYHCSMl9ZVbyFRA',
        'content-type': 'application/json',
        'priority': 'u=1, i',
        'referer': 'https://seller.wildberries.ru/dynamic-product-categories/delivery',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        # 'cookie': 'external-locale=ru; wbx-validation-key=a05aea94-1f15-4a6b-a879-91214ab6208f; _ym_uid=1706558827848753951; wb-pid=gYFVNmiV-ClBWLbziF3mRCivAAABjuat73-NyqrV1SGWhaUffhp6Urcc5xtuxVL0cGUy919g2hV-zQ; _ga=GA1.1.15166272.1716875082; upstream-cluster-uuid=ru; wb-id=gYFGSCFJ3zlHoKwPVBuDkd8NAAABkhrt3vPPKMFKWRgBJmzE-Ug2NVmCf-QNFfUffIuugHxihQbPkmRlYjc2NWFjLTcwYzAtNGY4My04N2FmLTAyOTI3MjY0MjMwMg; locale=ru; _wbauid=9366149821731088077; cfidsw-wb=WWHCunH5Nmc7GWW2QYyk2p4gerlt+bx7uegVeivxBxV7uLE4wj2jYMYjltVbtJBxsPiRANVnaIqHSm7KwJDq7URtNZxYO7DiwCcVJrhYLaGqs1d5A/hGNgcmJNkNO/lmLzrKX93nw5U4fOZO13JvF+p8brXQ986AUiymq8w8/g==; cfidsw-wb=WWHCunH5Nmc7GWW2QYyk2p4gerlt+bx7uegVeivxBxV7uLE4wj2jYMYjltVbtJBxsPiRANVnaIqHSm7KwJDq7URtNZxYO7DiwCcVJrhYLaGqs1d5A/hGNgcmJNkNO/lmLzrKX93nw5U4fOZO13JvF+p8brXQ986AUiymq8w8/g==; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UxQGgkaEdbIzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwcGH1tKlULDV0+RmllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVQCw0ZcXR2eFxsHx9jeRUoTFlTeSYhGDEpWAs9QRRwSl9vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwgZk1bJklZT3smHw1pN2wXPHVlLwkxLGJ5MVIvE0tsP0caRFpbQDsyVghDQE1HFF9BWncyUlFRS2EQR0lrZU5TQixmG3EVTQgNND1aciIPWzklWAgSPwsmIBR+cSVWDQ9dP0Jzbxt/Nl0cOWMRCxl+OmNdRkc3FSR7dSYKCTU3YnAvTCB7SykWRxsyYV5GaXUVWDo+YnBCcywmP2YjGERdJnkSSjMsG0V0JytYf0Bbb0dvLDA+VxlRDxZhDhYYRRcje0I3Yhk4QhgvPV8/YngiD2lIYCJKW08IKx0ZfnQqS3FPLH12X30beylOIA0lVBMhP05yASz5mw==; __zzatw-wb=MDA0dC0cTHtmcDhhDHEWTT17CT4VHThHKHIzd2UxQGgkaEdbIzVRP0FaW1Q4NmdBEXUmCQg3LGBwVxlRExpceEdXeiwcGH1tKlULDV0+RmllbQwtUlFRS19/Dg4/aU5ZQ11wS3E6EmBWGB5CWgtMeFtLKRZHGzJhXkZpdRVQCw0ZcXR2eFxsHx9jeRUoTFlTeSYhGDEpWAs9QRRwSl9vG3siXyoIJGM1Xz9EaVhTMCpYQXt1J3Z+KmUzPGwgZk1bJklZT3smHw1pN2wXPHVlLwkxLGJ5MVIvE0tsP0caRFpbQDsyVghDQE1HFF9BWncyUlFRS2EQR0lrZU5TQixmG3EVTQgNND1aciIPWzklWAgSPwsmIBR+cSVWDQ9dP0Jzbxt/Nl0cOWMRCxl+OmNdRkc3FSR7dSYKCTU3YnAvTCB7SykWRxsyYV5GaXUVWDo+YnBCcywmP2YjGERdJnkSSjMsG0V0JytYf0Bbb0dvLDA+VxlRDxZhDhYYRRcje0I3Yhk4QhgvPV8/YngiD2lIYCJKW08IKx0ZfnQqS3FPLH12X30beylOIA0lVBMhP05yASz5mw==; _ym_d=1739104555; neuromarket-captcha-token=MXwxfDE3MzE1MTM3NzJ8QUE9PXxmYzk0YWNmNDNhYzQ0ZTg3YTE1YWUxOGVlMmIwMjQzNnxuVDJRalBkNEJ6QTFwczF4ZzlvMGpEd1ZpSWdzZTdCUnhsUUNYRXBtdUNS; current_feature_version=E598F9C9-A7B9-478E-BBCD-A8B4DAD79DD9; neuromarket-token=ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBZWFFpT2pFM05ETTBPVFkzT1Rjc0luWmxjbk5wYjI0aU9qSXNJblZ6WlhJaU9pSTROVE0zT1RBeU5DSXNJbk5vWVhKa1gydGxlU0k2SWpNaUxDSmpiR2xsYm5SZmFXUWlPaUozWWlJc0luTmxjM05wYjI1ZmFXUWlPaUk0TXpWbU1tRTVORFJrWVRrMFpEY3hZbUV5T0dNMk1qVmlObVEzWVRWaVlpSXNJblZ6WlhKZmNtVm5hWE4wY21GMGFXOXVYMlIwSWpveE5qYzBNVEl5TURFekxDSjJZV3hwWkdGMGFXOXVYMnRsZVNJNkltSXpOems0WlRnNU5qTTNZalZtTjJJNU5UWTFZbVUxWXpsbE9ETTBZbVEyWm1KaE9Ua3hORFkzT0dVeU56QmhNR0kxWVdFME5qQXlNR05tTW1Sak1tSWlMQ0p3YUc5dVpTSTZJbTVDUlVWaFZVZFZVR1JQV0ZvNVYzZDNTM1U0TUZFOVBTSjkubVM1U1U0Wml2TXhxQmxnT1MtdVhlU0pEWUcxeVdEOWFraW9vSDNkc1FUaVFlcTZQU3FITEt0MjE0RXJvRERDcThacTdIaXNDdHBJMk5kMlBYd1NlOGpQRGVOQzJoSU51RUkyalBjMGRtaFVKbWJfTVBKMUxBRzB6aDlIVTlXUVdLeDE0TjFSYnktc3J2aVhWTTd1bUZMdjlzWHllRjIyU1lXTGRvT0VCN3FhejBwVDhLaFRIU2hCd0ozdVV3NUQwRFNBclR6cHZsclY0Uk5VRnVYNVZrTzM4MElUMTR0YlJHNTN1QnZkdGVjM05HdjNFUnhrX2hHNHVoUGFIbXJsVWZJRHp3M0tFQ1RKd1JaVDNoU1NXc3JmZW93MVExRE1nZlhabHZpNy0ycmFjZTdLc2h5aGhjR1gyZFVmWkpBX09CNnRFUmh1SnlvNHRpSmFjVUp3aGtn; WBTokenV3=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDM1OTA2NTQsInZlcnNpb24iOjIsInVzZXIiOiI4NTM3OTAyNCIsInNoYXJkX2tleSI6IjMiLCJjbGllbnRfaWQiOiJzZWxsZXItcG9ydGFsIiwic2Vzc2lvbl9pZCI6IjE0MmZkYzk1Y2FiMjRiZDk5NDYwMTg3YmZlZGZmYWM5IiwidXNlcl9yZWdpc3RyYXRpb25fZHQiOjE2NzQxMjIwMTMsInZhbGlkYXRpb25fa2V5IjoiYjM3OThlODk2MzdiNWY3Yjk1NjViZTVjOWU4MzRiZDZmYmE5OTE0Njc4ZTI3MGEwYjVhYTQ2MDIwY2YyZGMyYiJ9.QY87TYUI4FD8CPWhvmuZ-8S4kOs76L6g_9h9nESfIMvSK1HQV9CcfwoiGSHPEQ3Ucvi8nbvhxGVcAl7N0rq6EIGwDquhjySFjoHBTZ_8gkxVbHcWn4-2peqe3_cqL7ovXTv6Qe4R8VdzpgTMFsruFx0UUg37ZJm5CVHR0YbqZq22EbpAP-ZWxX-Z3Ti9WpBbfwHIDD3hIni0lKO8g_iiaQU8nAu5x6AdMwgMoZNgP7XLEzZPFjyZnQRNInydmv-vyAu0CQ7TBB7p_4rhaXCejqXxO1_w03L0dH9dHVfT1HK4UMrSaHRrIaXrlLfgt7gTjNUgGrltYHCSMl9ZVbyFRA; neuromarket-auth-v3=ZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBZWFFpT2pFM05ETTFPVEEyTlRRc0luWmxjbk5wYjI0aU9qSXNJblZ6WlhJaU9pSTROVE0zT1RBeU5DSXNJbk5vWVhKa1gydGxlU0k2SWpNaUxDSmpiR2xsYm5SZmFXUWlPaUp6Wld4c1pYSXRjRzl5ZEdGc0lpd2ljMlZ6YzJsdmJsOXBaQ0k2SWpFME1tWmtZemsxWTJGaU1qUmlaRGs1TkRZd01UZzNZbVpsWkdabVlXTTVJaXdpZFhObGNsOXlaV2RwYzNSeVlYUnBiMjVmWkhRaU9qRTJOelF4TWpJd01UTXNJblpoYkdsa1lYUnBiMjVmYTJWNUlqb2lZak0zT1RobE9EazJNemRpTldZM1lqazFOalZpWlRWak9XVTRNelJpWkRabVltRTVPVEUwTmpjNFpUSTNNR0V3WWpWaFlUUTJNREl3WTJZeVpHTXlZaUo5LlFZODdUWVVJNEZEOENQV2h2bXVaLThTNGtPczc2TDZnXzloOW5FU2ZJTXZTSzFIUVY5Q2Nmd29pR1NIUEVRM1Vjdmk4bmJ2aHhHVmNBbDdOMHJxNkVJR3dEcXVoanlTRmpvSEJUWl84Z2t4VmJIY1duNC0ycGVxZTNfY3FMN292WFR2NlFlNFI4VmR6cGdUTUZzcnVGeDBVVWczN1pKbTVDVkhSMFlicVpxMjJFYnBBUC1aV3hYLVozVGk5V3BCYmZ3SElERDNoSW5pMGxLTzhnX2lpYVFVOG5BdTV4NkFkTXdnTW9aTmdQN1hMRXpaUEZqeVpuUVJOSW55ZG12LXZ5QXUwQ1E3VEJCN3BfNHJoYVhDZWpxWHhPMV93MDNMMGRIOWRIVmZUMUhLNFVNclNhSFJySWFYcmxMZmd0N2dUak5VZ0dybHRZSENTTWw5WlZieUZSQQ%3D%3D; x-supplier-id=9cc7c16a-416a-47fe-b72d-d890e0b62a73; x-supplier-id-external=9cc7c16a-416a-47fe-b72d-d890e0b62a73; _ym_isad=1; _ga_N5X7KR2NQJ=GS1.1.1743633771.165.1.1743633789.0.0.0',
    }

    response = requests.get(
        'https://seller.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/weekly-rating',
        cookies=cookies,
        headers=headers,
    )

    response = response.json()
    # print(response)
    # return
    user = db.query(User).first()
    user.localization_index = response['data']['localization']['index']
    user.localization_percentage = float(response['data']['localization']['percent'])


    