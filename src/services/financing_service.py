from ..models.car import FinancingRequest, FinancingPlan


class FinancingService:
    INTEREST_RATE = 0.10
    MIN_YEARS = 3
    MAX_YEARS = 6
    
    def calculate_financing(self, request: FinancingRequest) -> FinancingPlan:
        if request.years < self.MIN_YEARS or request.years > self.MAX_YEARS:
            raise ValueError(f"El plazo debe ser entre {self.MIN_YEARS} y {self.MAX_YEARS} años")
        
        if request.down_payment >= request.car_price:
            raise ValueError("El enganche no puede ser mayor o igual al precio del auto")
        
        if request.down_payment < 0:
            raise ValueError("El enganche no puede ser negativo")
        
        loan_amount = request.car_price - request.down_payment
        monthly_rate = self.INTEREST_RATE / 12
        num_payments = request.years * 12
        
        if loan_amount > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = 0
        
        total_payment = monthly_payment * num_payments + request.down_payment
        total_interest = total_payment - request.car_price
        
        return FinancingPlan(
            car_price=request.car_price,
            down_payment=request.down_payment,
            loan_amount=loan_amount,
            years=request.years,
            monthly_payment=round(monthly_payment, 2),
            total_payment=round(total_payment, 2),
            total_interest=round(total_interest, 2),
            interest_rate=self.INTEREST_RATE
        )
    
    def get_financing_options(self, car_price: float, down_payment: float = None) -> list:
        if down_payment is None:
            down_payment = car_price * 0.20
        
        options = []
        for years in range(self.MIN_YEARS, self.MAX_YEARS + 1):
            try:
                request = FinancingRequest(
                    car_price=car_price,
                    down_payment=down_payment,
                    years=years
                )
                plan = self.calculate_financing(request)
                options.append(plan)
            except ValueError:
                continue
        
        return options