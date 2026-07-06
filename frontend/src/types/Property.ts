export interface Property {
  rank: number;
  id: string;
  city: string;
  zipCode: string;

  listing_price: number;
  estimated_rent: number;

  roi_pct: number;
  five_year_appreciation_pct: number;

  investment_score: number;

  square_feet: number;
  bedrooms: number;
  bathrooms: number;
  year_built: number;
  hoa_fee: number;

  median_income: number;
  bachelors_pct: number;
  median_home_value: number;
  owner_occupied_pct: number;
}