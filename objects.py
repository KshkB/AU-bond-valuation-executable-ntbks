class Bond:

    def __init__(self, face, price, coupon, time):
        
        self.fv = face 
        self.price = price 
        self.coupon = coupon
        self.time = time

    def value(self):
        return -self.price + (1 + self.coupon * self.time)*self.fv

    def value_yield(self):
        return self.value()/(self.price*self.time)

    def yld(self):
        return self.coupon * self.fv/self.price

    def infl_sprd(self):
        return (self.price-self.fv)/self.fv 

    def value_ip(self, lifetime_infl):
        sum_1 = -self.price
        sum_2 = self.fv*(1 + lifetime_infl)**(self.time-1)
        sum_3 = self.fv*self.coupon*((1 - lifetime_infl**self.time)/(1 - lifetime_infl))
        return sum_1 + sum_2 + sum_3

    def value_ip_yld(self, lifetime_infl):
        return self.value_ip(lifetime_infl)/(self.price*self.time)

