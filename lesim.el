(require 'generic-x)

(define-generic-mode 'lesim2-mode
  '("#")                       ; comment character
  '(
    "behaviors"                ; keywords
    "stimulus_elements" 
    "mechanism"
    "start_v"
    "start_w"
    "alpha_v"
    "alpha_w"
    "beta"
    "behavior_cost"
    "u"
    "response_requirements"
    "bind_trials"
    "n_subjects"
;;    "title"
    "subplottitle"
    "runlabel"
    "subject"
    "xscale"
    "xscale_match"
    "phases"
    "cumulative"
    "match"
    "filename"
    )                     ;; some keywords
  '(
    ;;; stop:
    ("stop:" . 'font-lock-builtin-face)
    ;;; stop:
    ("new_trial" . 'font-lock-keyword-face)
    ;;; @ commands:
    ("@\\<[a-z]*\\> " . 'font-lock-builtin-face)
    ;;; strings:
    ("'\\<.*?\\>'" . 'font-lock-string-face)
    ;;; LINEs
    ("\\<[A-Z]+[_A-Za-z0-9]*\\>" . 'font-lock-variable-name-face)
    ;;; various recurrent syntax fragments:
    ("_[[:blank:]\n]" . 'font-lock-constant-face)
    ("|" . 'font-lock-constant-face)
    ("->" . 'font-lock-constant-face)
;;    ("[+-]?[0-9]*\\.?[0-9]+" . 'font-lock-constant-face)
    )
  '("\\.ls2$") ; files for which to activate this mode 
  nil          ; other functions to call
  "A mode for lesim2 files" ; doc string
  )
