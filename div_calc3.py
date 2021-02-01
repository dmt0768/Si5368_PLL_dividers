def get_multiplier(fr_out: str, fr_in: str = '20000000', delta: float = 0.001, des_error: float = 0.1, max_error: float = 0.5, divider_limit : float = 5):

    # Initial parameters. All variables are named after the Si5368 Manual. But for comfortable coding NC1 is
    # named N1_LS, N2_LS

    f3_step = 1
    f3_min = 2500
    f3_max = 20000
    f3 = [2E3, 2E6]
    fosc = [4.85E9, 5.67E9]
    fosc_mid = (fosc[0] + fosc[1])/2
    flag = True
    res = {'N1_HS': 4, 'N1_LS': 1, 'N2_HS': 4, 'N2_LS': 2, 'N3': 1}
    fr_out = int(fr_out)
    fr_in = int(fr_in)

    def calc_N1_HS_N1_LS(res):  # Calculate N1_HS and N1_LS. N1_LS = NC1
        nonlocal flag
        while res['N1_HS'] <= 11:
            res['N1_LS'] = round(fosc_mid/(res['N1_HS'] * fr_out) / 2) * 2
            if round(fosc_mid/(res['N1_HS'] * fr_out)) == 1:
                res['N1_LS'] = 1
            if fosc[0] <= res['N1_HS'] * res['N1_LS'] * fr_out <=fosc[1]:
                return res

            res['N1_HS'] += 1
        flag = 'ERROR: calc_N1_HS_N1_LS'
        return res

    def calc_N3(res, ff3):  # Calculate N3
        nonlocal flag
        res['N3'] = round(fr_in / ff3)
        if f3[0] < fr_in / res['N3'] < f3[1]:
            return res
        flag = 'ERROR: calc_N3'
        return res

    def calc_N2_HS_N2_LS(res):  # Calculate N2_HS and N2_LS
        nonlocal flag
        f3_real = fr_in / res['N3']
        fosc_real = res['N1_HS'] * res['N1_LS'] * fr_out
        fosc_f3 = fosc_real / f3_real
        fosc_f3_errors = []
        while res['N2_HS'] <= 11:
            res['N2_LS'] = round(fosc_f3 / res['N2_HS'] / 2) * 2
            fosc_f3_real = res['N2_HS'] * res['N2_LS']
            fosc_f3_errors.append(abs(fosc_f3_real - fosc_f3))
            res['N2_HS'] += 1

        res['N2_HS'] = fosc_f3_errors.index(min(fosc_f3_errors)) + 4
        res['N2_LS'] = round(fosc_f3 / res['N2_HS'] / 2) * 2

        if fosc[0] < f3_real * res['N2_HS'] * res['N2_LS'] < fosc[1]:
            return res
        flag = 'ERROR: calc_N2_HS_N2_LS'
        return res

    def test_all(dictionary):  # Test of all coefficients
        nonlocal flag
        if flag == True:
            if not (4 <= dictionary['N1_HS'] <= 11):
                flag = 'Divider test №1 failed!'
            if not (1 <= dictionary['N1_LS'] <= 2 ** 20) and (
                    (dictionary['N1_LS'] % 2 == 0) or dictionary['N1_LS'] == 1):  # Проверь это условие!
                flag = 'Divider test №2 failed!'
            if not (4 <= dictionary['N2_HS'] <= 11):
                flag = 'Divider test №3 failed!'
            if not ((2 <= dictionary['N2_LS'] <= 2 ** 20) and dictionary['N2_LS'] % 2 == 0):
                flag = 'Divider test №4 failed!'
            if not (1 <= dictionary['N3'] <= 2 ** 19):
                flag = 'Divider test №5 failed!'

            #  Финальная проверка внутренних частот
            if not (2 * 10 ** 3 < (float(fr_in) / round(dictionary['N3'])) < 2 * 10 ** 6):
                # print('PLL in frequency test failed!')
                flag = 'PLL in frequency test failed!'

            if not (4.85 * 10 ** 9 <= (
                    float(fr_in) * round(dictionary['N2_HS']) * round(dictionary['N2_LS']) / round(dictionary['N3']))
                    <= 5.67 * 10 ** 9):
                # print('PLL out frequency test failed!')
                flag = 'PLL out frequency test failed!'

    def prepare_for_PLL_registers(dictionary):  # This function transforms real coefficients to ones whose are
                                                # wrote into the Si5368 registers.
        dictionary['N1_HS'] = dictionary['N1_HS'] - 4
        dictionary['N1_LS'] = dictionary['N1_LS'] - 1
        dictionary['N2_HS'] = dictionary['N2_HS'] - 4
        dictionary['N2_LS'] = dictionary['N2_LS'] - 1
        dictionary['N3'] = dictionary['N3'] - 1
        return dictionary

    # The main coder. It has many iterations from f3_min to f3_max with step g3_step. You can change the parameters if
    # the algorithm is so slow

    for i in range(f3_min, f3_max, f3_step):
        flag = True
        res = {'N1_HS': 4, 'N1_LS': 1, 'N2_HS': 4, 'N2_LS': 2, 'N3': 1}
        res = calc_N1_HS_N1_LS(res)
        res = calc_N3(res, i)
        res = calc_N2_HS_N2_LS(res)
        freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
        err = freq - float(fr_out)
        #print(err)
        if (abs(err) < max_error) and (flag is True):
            break

    #  One more testing, plus here is final error calculation
    freq = float(fr_in) * res['N2_HS'] * res['N2_LS'] / (res['N1_HS'] * res['N1_LS'] * res['N3'])
    err = freq - float(fr_out)
    if abs(err) > max_error:
        flag = 'calc error'
    test_all(res)
    res = prepare_for_PLL_registers(res)

    return [res, {'freq': freq, 'err': err, 'status': flag}]

    # There are 4 other channels whose you can adjust. You can't directly use this function. You have to send N1_LS
    # into this function. So write somewhere REAL (see prepare_for_PLL_registers) coefficients from get_multiplier()
    # and put the N1_LS into the get_secondary_get_multiplier().

def get_secondary_get_multiplier(main_fr_out, sec_fr_out, main_N1_LS):
    flag = True
    res = round(main_fr_out * main_N1_LS / sec_fr_out / 2) * 2
    if res != 0:
        freq = main_fr_out * main_N1_LS / res
        err = freq - sec_fr_out
    else:
        err = 'Zero result'
        freq = 0

    if not (1 <= res <= 2 ** 20) or not ((res % 2 == 0) or (res == 1)):
        flag = 'Failed'

    return [{'N1_LS': res - 1}, {'freq': freq, 'step_freq': main_fr_out * main_N1_LS, 'err': err, 'status': flag}]



# The main program has the cycle to test its functionality

if __name__ == '__main__':
    print(get_multiplier(str(550000000)))
    errors = 0
    right = 0

    '''
    for i in range(500000000, 600000000, 6250):
        ans = get_multiplier(str(i))
        if ans[1]['status'] is not True:
            #print(ans)
            print(i)
            errors += 1
            print(right / (right + errors) * 100, '%')
        else:
            right += 1'''