"""
Prerequisites: int<->str is slow, int<->decimal.Decimal is slow, decimal.Decimal<->str is fast.
decimal.Decimal needs configured decimal.Context to work with long ariphmetics.
"""
import decimal

decimal.setcontext(decimal.Context(prec=decimal.MAX_PREC, Emax=decimal.MAX_EMAX, Emin=decimal.MIN_EMIN, rounding=decimal.ROUND_DOWN))

TWO = decimal.Decimal(2)

"""
Performs str(int) faster.
Straightforward cast from int to decimal.Decimal is very slow too, so we will use Divide & Conquer method to do it asimptotically faster.
"""
def int_to_str(number: int) -> str:
    length = number.bit_length()
    if length <= 1024:
        return str(number)
    powers = {}
    def calc_power(length: int):
        if length in powers:
            return
        if length <= 1024:
            powers[length] = TWO ** length
        else:
            if length - 1 in powers:
                powers[length] = TWO * powers[length - 1]
            else:
                calc_power(length >> 1)
                calc_power((length + 1) >> 1)
                powers[length] = powers[length >> 1] * powers[(length + 1) >> 1]
    def int_to_decimal(number: int, length: int) -> decimal.Decimal:
        if length <= 1024:
            return decimal.Decimal(number)
        length_right = length >> 1
        if length_right not in powers:
            calc_power(length_right)
        left_value = number >> length_right
        right_value = number - (left_value << length_right)
        return int_to_decimal(left_value, length - length_right) * powers[length_right] + int_to_decimal(right_value, length_right)
    return str(int_to_decimal(number, number.bit_length()))

"""
Performs int(str) faster.
Let's do same Divide & Conquer as in int_to_str(), but we don't know bit length of number here, so we'll do it implicitly.
"""
def str_to_int(number: str) -> int:
    number = decimal.Decimal(number)
    cur_power = TWO ** 1024
    if number <= cur_power:
        return int(str(number))
    powers = []
    while cur_power <= number:
        powers.append(cur_power)
        cur_power = cur_power * cur_power
    blocks = [number]
    for block_len in reversed(powers):
        blocks = [part for block in blocks for part in divmod(block, block_len)]
    return int.from_bytes(b''.join(int(str(block)).to_bytes(128, byteorder='big') for block in blocks), byteorder='big')


def int_to_str_compare():
    import timeit, random
    for d in range(10, 28):
        x = (1 << (1 << d)) - 1
        start_time = timeit.default_timer()
        s = int_to_str(x)
        time_new = timeit.default_timer() - start_time
        print(f"n = 2^{1 << d} - 1")
        print(f"Время выполнения int_to_str(): {time_new:.3f} секунд")
        if d < 24:
            start_time = timeit.default_timer()
            s = str(x)
            time_old = timeit.default_timer() - start_time
            print(f"Время выполнения str(): {time_old:.3f} секунд")
            print(f"Коэффициент оптимизации: {time_old/time_new:.3f}")
        else:
            print(f"Время выполнения str(): слишком долго :)")

def str_to_int_compare():
    import timeit, random
    for d in range(10, 25):
        x = '1' + '0' * (1 << d)
        start_time = timeit.default_timer()
        s = str_to_int(x)
        time_new = timeit.default_timer() - start_time
        print(f"n = 10^{1 << d}")
        print(f"Время выполнения str_to_int(): {time_new:.3f} секунд")
        if d < 23:
            start_time = timeit.default_timer()
            s = int(x)
            time_old = timeit.default_timer() - start_time
            print(f"Время выполнения int(): {time_old:.3f} секунд")
            print(f"Коэффициент оптимизации: {time_old/time_new:.3f}")
        else:
            print(f"Время выполнения int(): слишком долго :)")

#print("int_to_str() vs int()")
#int_to_str_compare()
#print("str_to_int() vs str()")
#str_to_int_compare()
