Feature: Booking cancellation refund
  As a passenger, I can cancel within 24 hours of booking and receive a full refund

  @valid @id_R01
  Scenario: Cancel booking ABC123 (valid)
    Given a booking ABC123 booked at 2026-01-15T10:00:00Z
      And its payment status is "active"
      And the amount is 250.0
    When the passenger cancels at 2026-01-15T18:00:00Z
    Then a full refund is issued

  @valid @id_R02
  Scenario: Cancel booking QWE456 (valid)
    Given a booking QWE456 booked at 2026-01-14T08:00:00Z
      And its payment status is "active"
      And the amount is 175.5
    When the passenger cancels at 2026-01-16T09:00:00Z
    Then no refund is issued

  @edge @id_R03
  Scenario: Cancel booking RTY789 (edge)
    Given a booking RTY789 booked at 2026-01-10T00:00:00Z
      And its payment status is "active"
      And the amount is 99.99
    When the passenger cancels at 2026-01-11T00:00:00Z
    Then a full refund is issued

  @edge @id_R04
  Scenario: Cancel booking XYZ789 (edge)
    Given a booking XYZ789 booked at 2026-01-12T12:00:00Z
      And its payment status is "refunded"
      And the amount is 175.5
    When the passenger cancels at 2026-01-12T20:00:00Z
    Then no refund is issued

  @edge @id_R05
  Scenario: Cancel booking UIO234 (edge)
    Given a booking UIO234 booked at 2026-01-20T23:30:00Z
      And its payment status is "active"
      And the amount is 512.0
    When the passenger cancels at 2026-01-21T00:15:00Z
    Then a full refund is issued

  @adversarial @id_R06
  Scenario: Cancel booking PAS567 (adversarial)
    Given a cancellation request with missing or malformed fields
    When the passenger submits the cancellation for booking PAS567
    Then the request is rejected as invalid input
