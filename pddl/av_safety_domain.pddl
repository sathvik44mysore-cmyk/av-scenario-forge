; AV Safety Scenario Domain
; Models safety-critical properties that a test scenario must cover.
; Used by Fast Downward to verify that a generated scenario achieves
; full coverage of the required safety properties.

(define (domain av-safety)

  (:requirements :typing :strips :negative-preconditions)

  (:types
    safety-property   ; individual safety property (night, rain, pedestrian, etc.)
    scenario          ; the test scenario being constructed
  )

  (:predicates
    (property-required ?p - safety-property)    ; this property must be covered
    (property-covered  ?p - safety-property)    ; this property is satisfied in scenario
    (compatible        ?p1 - safety-property
                       ?p2 - safety-property)   ; two properties can coexist
    (scenario-active   ?s - scenario)
  )

  ; Cover a safety property in the active scenario
  (:action cover-property
    :parameters (?s - scenario ?p - safety-property)
    :precondition (and
      (scenario-active ?s)
      (property-required ?p)
      (not (property-covered ?p))
    )
    :effect (property-covered ?p)
  )

)
