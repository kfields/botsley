//
//Blocks World
//

namespace BwBrainTest

    brain BloxBrain

        predicate isClear(bool)

        method BloxBrain(bloxBrain)
        
            context BloxContext

                Table1 :Table
                    isClear true

                Block1 :Block
                    onTop Table1

                Block2 :Block
                    onTop Block1

                Block3 :Block
                    onTop Block2
                    isClear true

                stack Block1 :on Block2

                stack Block2 :on Block3

            blox :context BloxContext


        expert Blox

            method Blox(blox)
                
            method Impasse()
                where
                    [$g :Goal] status Active
                    -->
                    * @ /$g
                    !==>
                    halt
                    
            method GoalElab(+ [$g :Goal])
                + $g status Active

            method NotGoalElab(- [$g :Goal])
                - $g status Active
                    
            method Stack(stack $x :on $y -> $g)
                where
                    ! $x isClear true
                    -->
                    /clear $x
                    ==>
                    return
                //else
                where
                    ! $y isClear true
                    -->
                    /clear $y
                    ==>
                    return
                //else
                
                where
                    $x onTop $z
                    -->
                    - $x onTop $z
                    
                + $x onTop $y
                
                - $g

            method Clear(clear $x)
                where
                    $x beneath $y
                    $z isClear true
                    $z != $x
                    $z != $y
                    -->
                    * /stack $y :on $z

            method NotOnTopElab(- $x onTop $y)
                - $y beneath $x
                + $y isClear true

            method OntopElab(+ $x onTop $y)
                where
                    <$y :Block> isClear true
                    -->
                    - $y isClear true
                where
                    $x onTop $y
                    -->
                    + $y beneath $x

